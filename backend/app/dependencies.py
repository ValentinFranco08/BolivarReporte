"""Construir los servicios con sus colaboradores. Es la frontera con FastAPI."""
from functools import lru_cache
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from .core.config import settings
from .infrastructure.storage import LocalFileStorage
from .infrastructure.unit_of_work import UnitOfWork
from .infrastructure.predictor import LazyPredictor
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


@lru_cache(maxsize=1)
def get_predictor():
    """Una instancia por proceso; los pesos se cargan al inicializarla."""
    return LazyPredictor()


@lru_cache(maxsize=1)
def get_storage():
    return LocalFileStorage(settings.uploads_dir)


def get_category_service(db: Session = Depends(get_db)):
    return CategoryService(
        categories=CategoryRepository(db), reports=ReportRepository(db), unit_of_work=UnitOfWork(db),
    )


def get_classification_service(db: Session = Depends(get_db),
                               model=Depends(get_predictor), files=Depends(get_storage)):
    return ClassificationService(predictor=model, categories=CategoryRepository(db), storage=files)


def get_report_service(db: Session = Depends(get_db),
                       model=Depends(get_predictor), files=Depends(get_storage)):
    # Los repositorios comparten la misma sesión y la confirmación ocurre en el servicio.
    return ReportService(
        reports=ReportRepository(db), categories=get_category_service(db), users=UserRepository(db),
        predictions=PredictionRepository(db), feedback=FeedbackRepository(db),
        classification=get_classification_service(db, model, files), unit_of_work=UnitOfWork(db),
    )


def get_feedback_service(db: Session = Depends(get_db)):
    return FeedbackService(
        feedback=FeedbackRepository(db), predictions=PredictionRepository(db), unit_of_work=UnitOfWork(db),
    )


def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(users=UserRepository(db), unit_of_work=UnitOfWork(db))


def get_matching_service(db: Session = Depends(get_db)):
    return MatchingService(reports=ReportRepository(db))


def get_remum_service(db: Session = Depends(get_db), files=Depends(get_storage)):
    return RemumService(
        records=RemumRepository(db), reports=ReportRepository(db), users=UserRepository(db),
        storage=files, unit_of_work=UnitOfWork(db),
    )
