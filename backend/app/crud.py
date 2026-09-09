from sqlalchemy.orm import Session
from . import models, schemas, auth

# --- Users ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(name=user.name, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

import json
import math
from typing import List, Optional

# --- Categories ---
def get_categories(db: Session, only_verified: bool = False):
    query = db.query(models.Category).filter(models.Category.active == True)
    if only_verified:
        query = query.filter(models.Category.is_verified == True)
    return query.all()

def get_category_by_id(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_category_by_name(db: Session, name: str):
    return db.query(models.Category).filter(models.Category.name == name).first()

def get_pending_categories(db: Session):
    """Obtiene categorías propuestas por la IA que aún no fueron validadas por un admin."""
    return (
        db.query(models.Category)
        .filter(models.Category.active == True, models.Category.is_verified == False)
        .order_by(models.Category.created_at.desc())
        .all()
    )

def create_or_get_novel_category(
    db: Session,
    name: str,
    area: str,
    description: Optional[str] = None,
    embedding: Optional[List[float]] = None
):
    """Crea una categoría nueva sugerida por IA o retorna la existente."""
    existing = get_category_by_name(db, name)
    if existing:
        return existing
        
    centroid_json = json.dumps(embedding) if embedding else None
    cat = models.Category(
        name=name,
        area=area,
        description=description,
        is_verified=False,
        embedding_centroid=centroid_json,
        sample_count=1,
        active=True
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

def update_category_centroid(db: Session, category_id: int, new_embedding: List[float]):
    """
    Actualización en caliente (Online Memory):
    Calcula el promedio ponderado del centroide:
    c_new = (N * c_old + e) / (N + 1), normalizado a norma unitaria.
    """
    category = get_category_by_id(db, category_id)
    if not category:
        return None

    if not category.embedding_centroid:
        # Inicializa con el vector unitario
        norm = math.sqrt(sum(x * x for x in new_embedding)) or 1.0
        normalized = [x / norm for x in new_embedding]
        category.embedding_centroid = json.dumps(normalized)
        category.sample_count = 1
    else:
        old_centroid = json.loads(category.embedding_centroid)
        n = category.sample_count or 1
        
        # Promedio ponderado
        updated = [n * o + n_val for o, n_val in zip(old_centroid, new_embedding)]
        norm = math.sqrt(sum(x * x for x in updated)) or 1.0
        normalized = [x / norm for x in updated]
        
        category.embedding_centroid = json.dumps(normalized)
        category.sample_count = n + 1

    db.commit()
    db.refresh(category)
    return category

def approve_category(
    db: Session,
    category_id: int,
    name: Optional[str] = None,
    area: Optional[str] = None,
    description: Optional[str] = None
):
    """Aprueba oficialmente una categoría sugerida por IA."""
    cat = get_category_by_id(db, category_id)
    if not cat:
        return None
    cat.is_verified = True
    if name:
        cat.name = name
    if area:
        cat.area = area
    if description:
        cat.description = description
    db.commit()
    db.refresh(cat)
    return cat

def merge_categories(
    db: Session,
    source_category_id: int,
    target_category_id: Optional[int] = None,
    target_category_name: Optional[str] = None
):
    """
    Fusiona dos categorías (ej: 'crater' -> 'bache'):
    Reasigna todos los reportes de source a target, combina centroides y desactiva source.
    """
    source = get_category_by_id(db, source_category_id)
    if target_category_id:
        target = get_category_by_id(db, target_category_id)
    elif target_category_name:
        target = get_category_by_name(db, target_category_name)
    else:
        target = None

    if not source or not target:
        return None

    # Reasignar reportes
    db.query(models.Report).filter(models.Report.category_id == source_category_id).update(
        {models.Report.category_id: target_category_id}
    )

    # Combinar centroides si ambos existen
    if source.embedding_centroid and target.embedding_centroid:
        src_centroid = json.loads(source.embedding_centroid)
        tgt_centroid = json.loads(target.embedding_centroid)
        n_src = source.sample_count or 1
        n_tgt = target.sample_count or 1
        
        combined = [
            n_src * s + n_tgt * t
            for s, t in zip(src_centroid, tgt_centroid)
        ]
        norm = math.sqrt(sum(x * x for x in combined)) or 1.0
        normalized = [x / norm for x in combined]
        target.embedding_centroid = json.dumps(normalized)
        target.sample_count = n_src + n_tgt

    source.active = False
    db.commit()
    db.refresh(target)
    return target

# --- Reports ---
def get_reports(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Report).order_by(models.Report.created_at.desc()).offset(skip).limit(limit).all()

def get_report(db: Session, report_id: int):
    return db.query(models.Report).filter(models.Report.id == report_id).first()

def create_report(
    db: Session,
    report: schemas.ReportCreate,
    image_path: str,
    user_id: int = None,
    is_novel_category: bool = False,
    embedding: Optional[List[float]] = None
):
    embedding_json = json.dumps(embedding) if embedding else None
    db_report = models.Report(
        description=report.description,
        latitude=report.latitude,
        longitude=report.longitude,
        address=report.address,
        category_id=report.category_id,
        image_path=image_path,
        user_id=user_id,
        is_novel_category=is_novel_category,
        embedding=embedding_json
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def update_report_status(db: Session, report_id: int, status: models.ReportStatus):
    report = get_report(db, report_id)
    if report:
        report.status = status
        db.commit()
        db.refresh(report)
    return report

def update_report(db: Session, report_id: int, status: models.ReportStatus, priority: models.ReportPriority = None):
    report = get_report(db, report_id)
    if report:
        report.status = status
        if priority:
            report.priority = priority
        db.commit()
        db.refresh(report)
    return report

# --- AIPrediction ---
def get_model_version(db: Session, version_name: str = "multimodal-v1"):
    return db.query(models.ModelVersion).filter(models.ModelVersion.name == version_name).first()

def create_ai_prediction(db: Session, prediction: schemas.AIPredictionBase, report_id: int):
    db_prediction = models.AIPrediction(
        report_id=report_id,
        model_version_id=prediction.model_version_id,
        predicted_class=prediction.predicted_class,
        confidence=prediction.confidence
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

# --- Feedback ---
def get_feedback_for_prediction(db: Session, prediction_id: int):
    return db.query(models.Feedback).filter(models.Feedback.prediction_id == prediction_id).first()

def create_or_update_feedback(db: Session, prediction_id: int, correct: bool, correct_class: str | None, reviewer_id: int):
    existing = get_feedback_for_prediction(db, prediction_id)
    if existing:
        existing.correct = correct
        existing.correct_class = correct_class
        existing.reviewed_by = reviewer_id
        db.commit()
        db.refresh(existing)
        return existing
    fb = models.Feedback(
        prediction_id=prediction_id,
        correct=correct,
        correct_class=correct_class,
        reviewed_by=reviewer_id
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb

def get_all_feedback(db: Session):
    """Retorna todo el feedback con datos suficientes para reentrenamiento."""
    return (
        db.query(models.Feedback)
        .join(models.AIPrediction)
        .join(models.Report)
        .all()
    )

def get_unretrained_feedback(db: Session):
    """Retorna solo el feedback no procesado aún en ciclos de fine-tuning."""
    return (
        db.query(models.Feedback)
        .filter(models.Feedback.used_for_retraining == False)
        .join(models.AIPrediction)
        .join(models.Report)
        .all()
    )

def mark_feedback_retrained(db: Session, feedback_ids: List[int]):
    """Marca una lista de registros de feedback como ya utilizados en reentrenamiento."""
    if feedback_ids:
        db.query(models.Feedback).filter(models.Feedback.id.in_(feedback_ids)).update(
            {models.Feedback.used_for_retraining: True}, synchronize_session=False
        )
        db.commit()

