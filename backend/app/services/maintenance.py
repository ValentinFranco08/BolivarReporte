"""Operaciones explícitas de datos, fuera del arranque HTTP."""
import json
from .. import models
from ..security.credentials import get_password_hash
from ml.taxonomy import SEED_CATEGORIES
from .matching import MatchingPolicy

class BootstrapService:
    def __init__(self, categories, users, predictions, unit_of_work):
        self.categories = categories
        self.users = users
        self.predictions = predictions
        self.unit_of_work = unit_of_work

    def seed(self, demo_users=False):
        with self.unit_of_work:
            for data in SEED_CATEGORIES:
                if self.categories.by_name(data["name"]) is None:
                    self.categories.add(models.Category(**data, active=True, is_verified=True, sample_count=1))
            if self.predictions.model_version() is None:
                self.predictions.add_version(models.ModelVersion(name="multimodal-v1", version="1.0",
                    architecture="ViT + RoBERTa + Cross-Attention"))
            if demo_users:
                for name, email, password, role in (
                    ("Administrador Municipal", "admin@bolivar.gob.ar", "admin123", models.UserRole.ADMIN),
                    ("Vecino Bolívar", "vecino@bolivar.gob.ar", "vecino123", models.UserRole.CITIZEN),
                ):
                    if self.users.by_email(email) is None:
                        self.users.add(models.User(name=name, email=email, role=role,
                            password_hash=get_password_hash(password)))

class ReindexService:
    def __init__(self, reports, predictor, storage, unit_of_work):
        self.reports = reports
        self.predictor = predictor
        self.storage = storage
        self.unit_of_work = unit_of_work

    def run(self, legacy=False):
        updated = 0
        with self.unit_of_work:
            for report in self.reports.with_images():
                try:
                    vector = json.loads(report.embedding or "null")
                except ValueError:
                    vector = None
                identity = (not legacy and getattr(self.predictor, "pet_reid_enabled", False) is True
                            and report.pet_type == models.PetType.PERRO
                            and report.report_type in MatchingPolicy.SEARCHABLE_TYPES)
                if not identity and (isinstance(vector, list) and len(vector) == 768
                                     or isinstance(vector, dict) and not legacy):
                    continue
                try:
                    image = self.storage.read(report.image_path)
                except FileNotFoundError:
                    continue
                try:
                    result = (self.predictor.pet_identity_embedding(image) if identity
                              else self.predictor.extract_pet_embedding(image))
                except OSError:
                    continue
                if result:
                    report.embedding = json.dumps(result)
                    if identity:
                        for photo in report.additional_photos:
                            try:
                                extra = self.predictor.pet_identity_embedding(self.storage.read(photo.image_path))
                            except OSError:
                                continue
                            photo.embedding = json.dumps(extra)
                    updated += 1
        return updated
