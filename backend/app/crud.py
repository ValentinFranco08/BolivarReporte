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
    
    # Extraer campos de animal si vienen en el schema
    report_type = getattr(report, "report_type", models.AnimalReportType.PERDIDO)
    pet_type = getattr(report, "pet_type", models.PetType.PERRO)
    pet_name = getattr(report, "pet_name", None)
    pet_breed = getattr(report, "pet_breed", None)
    color_description = getattr(report, "color_description", None)
    health_status = getattr(report, "health_status", models.PetHealthStatus.SANO)
    contact_name = getattr(report, "contact_name", None)
    contact_phone = getattr(report, "contact_phone", None)
    is_resolved = getattr(report, "is_resolved", False) or False

    db_report = models.Report(
        description=report.description,
        latitude=report.latitude,
        longitude=report.longitude,
        address=report.address,
        category_id=report.category_id,
        image_path=image_path,
        user_id=user_id,
        is_novel_category=is_novel_category,
        embedding=embedding_json,
        report_type=report_type,
        pet_type=pet_type,
        pet_name=pet_name,
        pet_breed=pet_breed,
        color_description=color_description,
        health_status=health_status,
        contact_name=contact_name,
        contact_phone=contact_phone,
        is_resolved=is_resolved
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_active_danger_alerts(db: Session):
    """Obtiene alertas activas de cebos tóxicos o peligro inminente."""
    return db.query(models.Report).filter(
        models.Report.report_type == models.AnimalReportType.ALERTA_CEBO,
        models.Report.is_resolved == False
    ).order_by(models.Report.created_at.desc()).all()

def find_candidate_pet_matches(db: Session, target_report: models.Report, top_k: int = 5) -> List[dict]:
    """
    Busca coincidencias de mascotas por similitud visual, rasgos semánticos y distancia en Bolívar.
    Si el reporte es PERDIDO -> busca en ENCONTRADO / EN_TRANSITO.
    Si el reporte es ENCONTRADO -> busca en PERDIDO.
    """
    from .ai_service import (
        calculate_cosine_similarity,
        haversine_km,
        calculate_pet_match_score,
        calculate_semantic_similarity
    )

    if not target_report.embedding:
        return []
    try:
        target_emb = json.loads(target_report.embedding)
    except Exception:
        return []

    # Determinar qué tipos contrastar
    target_type = str(target_report.report_type.value if hasattr(target_report.report_type, 'value') else target_report.report_type)
    if target_type == "perdido":
        opposite_types = [models.AnimalReportType.ENCONTRADO, models.AnimalReportType.EN_TRANSITO]
    elif target_type in ("encontrado", "en_transito"):
        opposite_types = [models.AnimalReportType.PERDIDO]
    else:
        opposite_types = [models.AnimalReportType.PERDIDO, models.AnimalReportType.ENCONTRADO]

    candidates = db.query(models.Report).filter(
        models.Report.id != target_report.id,
        models.Report.report_type.in_(opposite_types),
        models.Report.pet_type == target_report.pet_type,
        models.Report.is_resolved == False,
        models.Report.embedding.isnot(None)
    ).all()

    scored_candidates = []
    for cand in candidates:
        try:
            cand_emb = json.loads(cand.embedding)
            vis_sim = calculate_cosine_similarity(target_emb, cand_emb)
            dist_km = haversine_km(target_report.latitude, target_report.longitude, cand.latitude, cand.longitude)
            
            # Comparar rasgos semánticos de pelaje, raza y descripción
            sem_sim = calculate_semantic_similarity(
                target_color=target_report.color_description,
                target_breed=target_report.pet_breed,
                target_desc=target_report.description,
                cand_color=cand.color_description,
                cand_breed=cand.pet_breed,
                cand_desc=cand.description
            )
            
            score = calculate_pet_match_score(vis_sim, dist_km, semantic_sim=sem_sim, max_radius_km=5.0)

            # Candidato válido si la similitud visual es relevante o el score combinado supera el umbral
            if vis_sim >= 0.25 or (vis_sim > 0.15 and sem_sim >= 0.70):
                scored_candidates.append({
                    "report": cand,
                    "visual_similarity": round(vis_sim, 3),
                    "semantic_similarity": round(sem_sim, 3),
                    "distance_km": dist_km,
                    "combined_score": score
                })
        except Exception as e:
            continue

    # Ordenar por score combinado descendente
    scored_candidates.sort(key=lambda x: x["combined_score"], reverse=True)
    return scored_candidates[:top_k]

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

# --- REMUM ---
import random
import string

def generate_qr_hash(length: int = 4):
    chars = string.ascii_uppercase + string.digits
    return "B-" + "".join(random.choice(chars) for _ in range(length))

def get_unique_qr_hash(db: Session) -> str:
    while True:
        qr_hash = generate_qr_hash()
        if not db.query(models.RemumRecord).filter(models.RemumRecord.qr_code_id == qr_hash).first():
            return qr_hash

def create_remum_record(db: Session, user_id: int, remum: schemas.RemumCreate, image_path: str = None):
    qr_code_id = get_unique_qr_hash(db)
    db_remum = models.RemumRecord(
        user_id=user_id,
        pet_name=remum.pet_name,
        pet_type=remum.pet_type,
        pet_breed=remum.pet_breed,
        color_description=remum.color_description,
        chip_number=remum.chip_number,
        is_community_pet=remum.is_community_pet,
        address=remum.address,
        qr_code_id=qr_code_id,
        image_path=image_path
    )
    db.add(db_remum)
    db.commit()
    db.refresh(db_remum)
    return db_remum

def get_remum_record_by_qr(db: Session, qr_code_id: str):
    return db.query(models.RemumRecord).filter(models.RemumRecord.qr_code_id == qr_code_id).first()

def add_health_event(db: Session, remum_id: int, event: schemas.HealthEventCreate):
    db_event = models.RemumHealthEvent(
        remum_record_id=remum_id,
        **event.model_dump()
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def add_godparent(db: Session, remum_id: int, godparent: schemas.GodparentCreate):
    db_gp = models.RemumGodparent(
        remum_record_id=remum_id,
        name=godparent.name,
        task=godparent.task
    )
    db.add(db_gp)
    db.commit()
    db.refresh(db_gp)
    return db_gp

def trigger_remum_panic(db: Session, qr_code_id: str, lat: float = None, lng: float = None):
    remum = get_remum_record_by_qr(db, qr_code_id)
    if not remum:
        return None
    
    # Cambiar estado a extraviado
    remum.status = models.RemumStatus.EXTRAVIADO
    
    # Crear reporte automaticamente
    db_report = models.Report(
        user_id=remum.user_id,
        description=f"¡ALERTA AUTOMÁTICA REMUM! {remum.pet_name} se extravió en la zona de {remum.address or 'Bolívar'}. Por favor prestar atención.",
        address=remum.address,
        latitude=lat or remum.latitude,
        longitude=lng or remum.longitude,
        image_path=remum.image_path or "", # o una imagen por defecto
        report_type=models.AnimalReportType.PERDIDO,
        pet_type=remum.pet_type,
        pet_name=remum.pet_name,
        pet_breed=remum.pet_breed,
        color_description=remum.color_description,
        health_status=models.PetHealthStatus.CON_COLLAR,
        contact_name=remum.user.name if remum.user else None,
        is_resolved=False,
        status=models.ReportStatus.REPORTADO,
        priority=models.ReportPriority.HIGH
    )
    db.add(db_report)
    db.commit()
    db.refresh(remum)
    return remum
