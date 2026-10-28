"""Composición de objetos; FastAPI solo interviene en esta frontera."""
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from .core.config import settings
from .infrastructure.storage import LocalFileStorage
from .infrastructure.unit_of_work import UnitOfWork
from .infrastructure.predictor import predictor
from .repositories.users import UserRepository
from .repositories.reports import ReportRepository
from .repositories.categories import CategoryRepository
from .repositories.predictions import PredictionRepository
from .repositories.feedback import FeedbackRepository
from .repositories.remum import RemumRepository
from .services.categories import CategoryService
from .services.classification import ClassificationService
from .services.reports import ReportService
from .services.authentication import AuthService
from .services.feedback import FeedbackService
from .services.remum import RemumService
from .services.matching import MatchingService

storage = LocalFileStorage(settings.uploads_dir)

def get_predictor():
    return predictor

def get_storage():
    return storage

def get_category_service(db: Session = Depends(get_db)):
    return CategoryService(CategoryRepository(db), ReportRepository(db), UnitOfWork(db))

def get_classification_service(db: Session = Depends(get_db),
        model=Depends(get_predictor), files=Depends(get_storage)):
    return ClassificationService(model, CategoryRepository(db), files)

def get_feedback_service(db: Session = Depends(get_db)):
    return FeedbackService(FeedbackRepository(db), PredictionRepository(db), UnitOfWork(db))

def get_report_service(db: Session = Depends(get_db),
        categories=Depends(get_category_service), classification=Depends(get_classification_service),
        feedback=Depends(get_feedback_service)):
    return ReportService(ReportRepository(db), categories, UserRepository(db),
        PredictionRepository(db), feedback, classification, UnitOfWork(db))

def get_auth_service(db: Session = Depends(get_db)):
    from . import auth
    return AuthService(UserRepository(db), auth, auth, UnitOfWork(db))

def get_matching_service(db: Session = Depends(get_db)):
    return MatchingService(ReportRepository(db))

def get_remum_service(db: Session = Depends(get_db), files=Depends(get_storage)):
    return RemumService(RemumRepository(db), ReportRepository(db), UserRepository(db), files, UnitOfWork(db))
