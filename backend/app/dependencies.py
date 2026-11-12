"""Construir los servicios con sus colaboradores. Es la frontera con FastAPI."""
from functools import lru_cache
from fastapi import Depends
from sqlalchemy.orm import Session
from .dao.database import get_db
from .config.settings import settings
from .integrations.storage import LocalFileStorage
from .dao.unit_of_work import UnitOfWork
from .integrations.ml_predictor import LazyPredictor
from .dao.users import UserDAO
from .dao.reports import ReportDAO
from .dao.categories import CategoryDAO
from .dao.predictions import PredictionDAO
from .dao.feedback import FeedbackDAO
from .dao.remum import RemumDAO
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
        categories=CategoryDAO(db), reports=ReportDAO(db), unit_of_work=UnitOfWork(db),
    )


def get_classification_service(db: Session = Depends(get_db),
                               model=Depends(get_predictor), files=Depends(get_storage)):
    return ClassificationService(predictor=model, categories=CategoryDAO(db), storage=files)


def get_report_service(db: Session = Depends(get_db),
                       model=Depends(get_predictor), files=Depends(get_storage)):
    # Los repositorios comparten la misma sesión y la confirmación ocurre en el servicio.
    return ReportService(
        reports=ReportDAO(db), categories=get_category_service(db), users=UserDAO(db),
        predictions=PredictionDAO(db), feedback=FeedbackDAO(db),
        classification=get_classification_service(db, model, files), unit_of_work=UnitOfWork(db),
    )


def get_feedback_service(db: Session = Depends(get_db)):
    return FeedbackService(
        feedback=FeedbackDAO(db), predictions=PredictionDAO(db), unit_of_work=UnitOfWork(db),
    )


def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(users=UserDAO(db), unit_of_work=UnitOfWork(db))


def get_matching_service(db: Session = Depends(get_db)):
    return MatchingService(reports=ReportDAO(db))


def get_remum_service(db: Session = Depends(get_db), files=Depends(get_storage)):
    return RemumService(
        records=RemumDAO(db), reports=ReportDAO(db), users=UserDAO(db),
        storage=files, unit_of_work=UnitOfWork(db),
    )
