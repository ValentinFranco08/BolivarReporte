"""Fachada de compatibilidad para scripts; el backend usa servicios y repositorios.

No añadir reglas de negocio aquí. Los nombres históricos delegan en los objetos nuevos.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from . import models, schemas
from .repositories.users import UserRepository
from .repositories.reports import ReportRepository
from .repositories.categories import CategoryRepository
from .repositories.predictions import PredictionRepository
from .repositories.feedback import FeedbackRepository
from .repositories.remum import RemumRepository
from .services.categories import CategoryService
from .services.matching import MatchingService
from .services.remum import QrCodeGenerator
from .infrastructure.unit_of_work import UnitOfWork
from .dependencies import (get_auth_service, get_feedback_service, get_category_service,
    get_classification_service, get_report_service, get_remum_service, storage, predictor)

def _reports(db):
    return get_report_service(db, get_category_service(db),
        get_classification_service(db, predictor, storage), get_feedback_service(db))

def get_user_by_email(db: Session, email: str):
    return UserRepository(db).by_email(email)

def create_user(db: Session, user: schemas.UserCreate):
    return get_auth_service(db).register(user)

def get_categories(db: Session, only_verified: bool=False):
    return CategoryRepository(db).list(only_verified)

def get_category_by_id(db: Session, category_id: int):
    return CategoryRepository(db).get(category_id)

def get_category_by_name(db: Session, name: str):
    return CategoryRepository(db).by_name(name)

def get_pending_categories(db: Session):
    return CategoryRepository(db).pending()

def create_or_get_novel_category(db: Session, name: str, area: str, description: Optional[str]=None, embedding: Optional[List[float]]=None):
    with UnitOfWork(db):
        result = get_category_service(db).create_or_get(name, area, description, embedding)
    return result

def update_category_centroid(db: Session, category_id: int, new_embedding: List[float]):
    with UnitOfWork(db):
        result = get_category_service(db).update_centroid(category_id, new_embedding)
    return result

def approve_category(db: Session, category_id: int, name: Optional[str]=None, area: Optional[str]=None, description: Optional[str]=None):
    with UnitOfWork(db):
        result = get_category_service(db).approve(category_id, name, area, description)
    return result

def merge_categories(db: Session, source_category_id: int, target_category_id: Optional[int]=None, target_category_name: Optional[str]=None):
    with UnitOfWork(db):
        result = get_category_service(db).merge(source_category_id, target_category_id, target_category_name)
    return result

def get_reports(db: Session, skip: int=0, limit: int=100):
    return ReportRepository(db).list(skip, limit)

def get_report(db: Session, report_id: int):
    return ReportRepository(db).get(report_id)

def create_report(db: Session, report: schemas.ReportCreate, image_path: str, user_id: int=None, is_novel_category: bool=False, embedding: Optional[List[float]]=None):
    with UnitOfWork(db):
        result = _reports(db).create_record(report, image_path, user_id, is_novel_category, embedding)
    return result

def get_active_danger_alerts(db: Session):
    return ReportRepository(db).active_alerts()

def find_candidate_pet_matches(db: Session, target_report: models.Report, top_k: int=5) -> List[dict]:
    return MatchingService(ReportRepository(db)).find(target_report, top_k)

def update_report_status(db: Session, report_id: int, status: models.ReportStatus):
    report = ReportRepository(db).get(report_id)
    if report is not None:
        with UnitOfWork(db):
            report.status = status
    return report

def update_report(db: Session, report_id: int, status: models.ReportStatus, priority: models.ReportPriority=None):
    report = ReportRepository(db).get(report_id)
    if report is not None:
        with UnitOfWork(db):
            report.status = status
            if priority is not None:
                report.priority = priority
    return report

def get_model_version(db: Session, version_name: str='multimodal-v1'):
    return PredictionRepository(db).model_version(version_name)

def create_ai_prediction(db: Session, prediction: schemas.AIPredictionBase, report_id: int):
    with UnitOfWork(db):
        result = PredictionRepository(db).add(models.AIPrediction(report_id=report_id, **prediction.model_dump(exclude={"is_novel_category", "similarity_score"})))
    return result

def get_feedback_for_prediction(db: Session, prediction_id: int):
    return FeedbackRepository(db).by_prediction(prediction_id)

def create_or_update_feedback(db: Session, prediction_id: int, correct: bool, correct_class: str | None, reviewer_id: int):
    with UnitOfWork(db):
        result = get_feedback_service(db).save(prediction_id, correct, correct_class, reviewer_id)
    return result

def get_all_feedback(db: Session):
    return FeedbackRepository(db).list()

def get_unretrained_feedback(db: Session):
    return FeedbackRepository(db).list(pending_only=True)

def mark_feedback_retrained(db: Session, feedback_ids: List[int]):
    with UnitOfWork(db):
        result = FeedbackRepository(db).mark_retrained(feedback_ids)
    return result

def generate_qr_hash(length: int=4):
    return QrCodeGenerator(None).generate(length)

def get_unique_qr_hash(db: Session) -> str:
    return QrCodeGenerator(RemumRepository(db)).unique()

def create_remum_record(db: Session, user_id: int, remum: schemas.RemumCreate, image_path: str=None):
    with UnitOfWork(db):
        result = get_remum_service(db, storage).create_record(user_id, remum, image_path)
    return result

def get_remum_record_by_qr(db: Session, qr_code_id: str):
    return RemumRepository(db).by_qr(qr_code_id)

def add_health_event(db: Session, remum_id: int, event: schemas.HealthEventCreate):
    with UnitOfWork(db):
        result = RemumRepository(db).add_related(models.RemumHealthEvent(remum_record_id=remum_id, **event.model_dump()))
    return result

def add_godparent(db: Session, remum_id: int, godparent: schemas.GodparentCreate):
    with UnitOfWork(db):
        result = RemumRepository(db).add_related(models.RemumGodparent(remum_record_id=remum_id, **godparent.model_dump()))
    return result

def trigger_remum_panic(db: Session, qr_code_id: str, lat: float=None, lng: float=None):
    record = RemumRepository(db).by_qr(qr_code_id)
    if record is None:
        return None
    with UnitOfWork(db):
        get_remum_service(db, storage).create_alert(record, lat, lng)
    return record
