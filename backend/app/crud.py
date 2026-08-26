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

# --- Categories ---
def get_categories(db: Session):
    return db.query(models.Category).filter(models.Category.active == True).all()

def get_category_by_name(db: Session, name: str):
    return db.query(models.Category).filter(models.Category.name == name).first()

# --- Reports ---
def get_reports(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Report).order_by(models.Report.created_at.desc()).offset(skip).limit(limit).all()

def get_report(db: Session, report_id: int):
    return db.query(models.Report).filter(models.Report.id == report_id).first()

def create_report(db: Session, report: schemas.ReportCreate, image_path: str, user_id: int = None):
    db_report = models.Report(
        description=report.description,
        latitude=report.latitude,
        longitude=report.longitude,
        address=report.address,
        category_id=report.category_id,
        image_path=image_path,
        user_id=user_id
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
