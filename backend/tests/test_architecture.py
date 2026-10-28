"""Casos de uso transaccionales, límites arquitectónicos y compatibilidad HTTP."""
import ast
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, MagicMock
import pytest
from app import models, schemas
from app.core.errors import PermissionDeniedError, ApplicationError
from app.dependencies import (get_report_service, get_category_service, get_classification_service,
                              get_feedback_service, get_remum_service, get_predictor, get_storage)
from app.infrastructure.storage import LocalFileStorage
from app.infrastructure.unit_of_work import UnitOfWork
from app.repositories.reports import ReportRepository
from app.services.reports import ReportService
from app.services.classification import ClassificationService
from app.main import app

ROOT = Path(__file__).resolve().parents[2]

class FakePredictor:
    ready = True
    model_version = "test-v1"

    def predict(self, image_bytes, text, category_centroids=None):
        return {"predictions": [{"label": "animal_perdido", "score": .9}],
                "classification": {"label": "animal_perdido"}, "model_version": self.model_version}

    def extract_pet_embedding(self, image_bytes):
        return [1.0, 0.0, 0.0]


def report_service(db, tmp_path):
    return get_report_service(db, get_category_service(db),
        get_classification_service(db, FakePredictor(), LocalFileStorage(tmp_path)), get_feedback_service(db))


def test_services_work_with_objects_without_http_or_weights():
    repository = Mock()
    report = SimpleNamespace(id=3, status="reportado", is_resolved=False)
    repository.get.return_value = report
    service = ReportService(repository, None, None, None, None, None, MagicMock())
    assert service.get(3) is report
    service.resolve(3)
    assert report.is_resolved is True
    assert report.status == models.ReportStatus.RESUELTO


def test_report_rolls_back_category_prediction_and_feedback(db, tmp_path, monkeypatch):
    db.add(models.ModelVersion(name="multimodal-v1", version="test"))
    db.commit()
    service = report_service(db, tmp_path)
    def fail(*args, **kwargs):
        raise RuntimeError("Fallo al guardar feedback")
    monkeypatch.setattr(service.feedback, "save", fail)
    with pytest.raises(RuntimeError, match="feedback"):
        service.create(schemas.ReportSubmission(image_path="/uploads/test.jpg", predicted_class="nueva",
            is_novel_category=True, embedding=[1, 0, 0]))
    assert db.query(models.Report).count() == 0
    assert db.query(models.AIPrediction).count() == 0
    assert db.query(models.Feedback).count() == 0
    assert db.query(models.Category).filter_by(name="nueva").count() == 0
    assert db.query(models.ModelVersion).count() == 1


def test_report_preserves_zero_confidence_and_does_not_mutate_submission(db, tmp_path):
    db.add(models.ModelVersion(name="multimodal-v1", version="test"))
    db.commit()
    submission = schemas.ReportSubmission(image_path="/uploads/test.jpg", predicted_class="nueva",
        is_novel_category=True, confidence=0, embedding=[1, 0, 0])
    report = report_service(db, tmp_path).create(submission)
    assert report.prediction.confidence == 0
    assert report.category.sample_count == 1
    assert submission.category_id is None
    assert db.query(models.Feedback).count() == 1


def test_merge_by_name_reassigns_reports(db):
    service = get_category_service(db)
    source = service.create_or_get("origen", "Animales")
    target = service.create_or_get("destino", "Animales")
    report = ReportRepository(db).add(models.Report(image_path="/uploads/test.jpg", category_id=source.id))
    with UnitOfWork(db):
        result = service.merge(source.id, target_category_name=target.name)
    assert result.id == target.id
    db.refresh(report)
    assert report.category_id == target.id
    assert not source.active


def test_centroid_rejects_mismatched_dimensions(db):
    service = get_category_service(db)
    category = service.create_or_get("vector", "Animales", embedding=[1, 0, 0])
    with pytest.raises(ApplicationError, match="dimensión"):
        service.update_centroid(category.id, [1, 0])


def test_remum_denied_alert_does_not_modify_data(db, tmp_path):
    owner = models.User(name="Dueño", email="owner@test.com", password_hash="unused")
    stranger = models.User(name="Otro", email="stranger@test.com", password_hash="unused")
    db.add_all([owner, stranger])
    db.commit()
    service = get_remum_service(db, LocalFileStorage(tmp_path))
    pet = service.create(schemas.RemumCreate(pet_name="Milo", latitude=-36, longitude=-61), owner)
    with pytest.raises(PermissionDeniedError):
        service.panic(pet.qr_code_id, stranger)
    db.refresh(pet)
    assert pet.status == models.RemumStatus.A_SALVO
    assert db.query(models.Report).count() == 0
    service.panic(pet.qr_code_id, owner, lat=0, lng=0)
    report = db.query(models.Report).one()
    assert report.latitude == 0 and report.longitude == 0


def test_remum_creation_preserves_coordinates(client, tmp_path):
    result = client.post("/api/auth/register", json={"name": "Tutor", "email": "tutor@test.com", "password": "password"})
    assert result.status_code == 200
    app.dependency_overrides[get_storage] = lambda: LocalFileStorage(tmp_path)
    try:
        result = client.post("/api/remum/", data={"pet_name": "Milo", "latitude": "0", "longitude": "0"})
    finally:
        app.dependency_overrides.pop(get_storage)
    assert result.status_code == 200
    assert result.json()["latitude"] == 0


def test_classification_can_use_an_injected_predictor_and_storage(tmp_path):
    categories = Mock()
    categories.list.return_value = []
    service = ClassificationService(FakePredictor(), categories, LocalFileStorage(tmp_path))
    result = service.classify(b"image", "Milo perdido", "image/jpeg")
    assert result["model_version"] == "test-v1"
    assert (tmp_path / Path(result["image_path"]).name).read_bytes() == b"image"
    with pytest.raises(ApplicationError):
        service.classify(b"image", "", None)


def test_failed_prediction_does_not_leave_uploaded_files(tmp_path):
    predictor = Mock()
    predictor.predict.return_value = {"error": "Modelo no disponible", "predictions": []}
    categories = Mock()
    categories.list.return_value = []
    service = ClassificationService(predictor, categories, LocalFileStorage(tmp_path))
    with pytest.raises(ApplicationError):
        service.classify(b"image", "", "image/jpeg")
    assert list(tmp_path.iterdir()) == []


def test_routes_are_unique_and_godparents_require_auth(client):
    from fastapi.routing import APIRoute
    from app.controllers import public, authentication, reports, feedback, categories, remum
    operations = [(route.path, method)
                  for controller in (public, authentication, reports, feedback, categories, remum)
                  for route in controller.router.routes if isinstance(route, APIRoute)
                  for method in route.methods]
    assert len(operations) == 25
    assert len(operations) == len(set(operations))
    result = client.post("/api/remum/B-TEST/padrinos", json={"name": "Tutor", "task": "Comida"})
    assert result.status_code == 401


def test_importing_api_does_not_load_torch():
    result = subprocess.run([sys.executable, "-c", "from app.main import app; import sys; assert 'torch' not in sys.modules"],
        cwd=ROOT, env={**__import__('os').environ, "PYTHONPATH": "backend:.", "DATABASE_URL": "sqlite:///:memory:"},
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_controllers_and_ml_respect_boundaries():
    for file in (ROOT / "backend/app/controllers").glob("*.py"):
        tree = ast.parse(file.read_text())
        assert not any(isinstance(node, ast.Attribute) and node.attr in ("query", "commit", "rollback", "flush")
                       for node in ast.walk(tree)), file
    for file in (ROOT / "ml").rglob("*.py"):
        if "datasets" in file.parts:
            continue  # Herramientas históricas de recolección.
        tree = ast.parse(file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith(("app.", "backend.", "fastapi", "sqlalchemy")), file
