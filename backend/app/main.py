import os
import shutil
import json
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid

from .ai_service import ai_service
from . import models, schemas, crud, auth, database

app = FastAPI(
    title="Reporte Bolívar — API",
    description="API para la plataforma inteligente de participación ciudadana de Bolívar.",
    version="2.0.0"
)

@app.on_event("startup")
def on_startup():
    try:
        models.Base.metadata.create_all(bind=database.engine)
        db = database.SessionLocal()
        try:
            count = db.query(models.Category).count()
            if count == 0:
                from ml.taxonomy import SEED_CATEGORIES
                print(f"🌱 Sembrando {len(SEED_CATEGORIES)} categorías iniciales...")
                for cat_data in SEED_CATEGORIES:
                    cat = models.Category(
                        name=cat_data["name"],
                        area=cat_data["area"],
                        description=cat_data.get("description", ""),
                        active=True,
                        is_verified=True,
                        sample_count=1
                    )
                    db.add(cat)
                db.commit()
                print("✅ Categorías iniciales sembradas.")

            # Sembrar usuarios por defecto si no existen
            if not db.query(models.User).filter_by(email="admin@bolivar.gob.ar").first():
                admin_user = models.User(
                    name="Administrador Municipal",
                    email="admin@bolivar.gob.ar",
                    password_hash=auth.get_password_hash("admin123"),
                    role=models.UserRole.ADMIN,
                )
                db.add(admin_user)
            if not db.query(models.User).filter_by(email="vecino@bolivar.gob.ar").first():
                vecino_user = models.User(
                    name="Vecino Bolívar",
                    email="vecino@bolivar.gob.ar",
                    password_hash=auth.get_password_hash("vecino123"),
                    role=models.UserRole.CITIZEN,
                )
                db.add(vecino_user)
            db.commit()
            print("✅ Usuarios iniciales verificados (admin@bolivar.gob.ar / vecino@bolivar.gob.ar).")
        finally:
            db.close()
    except Exception as e:
        print(f"⚠️ Advertencia inicializando base de datos en startup: {e}")

app.add_middleware(
    CORSMiddleware,
    # Orígenes permitidos configurables por entorno (separados por coma).
    # Por defecto, el dev server de Next en 3000.
    allow_origins=[
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if o.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# --- RUTAS PÚBLICAS ---

@app.get("/")
def read_root():
    return {"message": "Reporte Bolívar API v2.0 — Multimodal"}

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "model_ready": ai_service.ready,
        "model_version": ai_service.model_version if ai_service.ready else None,
    }

@app.get("/api/categories", response_model=List[schemas.CategoryResponse])
def get_categories(db: Session = Depends(database.get_db)):
    return crud.get_categories(db)


# --- AUTH ---

@app.post("/api/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    return crud.create_user(db=db, user=user)

@app.post("/api/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


# --- AI Y REPORTES ---

@app.post("/api/ai/predict")
async def predict(
    file: UploadFile = File(...),
    text: str = Form(default=""),
    db: Session = Depends(database.get_db),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen.")

    image_bytes = await file.read()
    
    # Guardar imagen temporalmente para que el front la referencie al guardar
    filename = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(UPLOADS_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(image_bytes)
        
    description = text.strip() if text else ""

    # Extraer centroides vectoriales de las categorías existentes en la base de datos
    centroids = []
    try:
        categories = crud.get_categories(db)
        for cat in categories:
            if cat.embedding_centroid:
                try:
                    c_vec = json.loads(cat.embedding_centroid)
                    centroids.append({
                        "id": cat.id,
                        "name": cat.name,
                        "area": cat.area,
                        "centroid": c_vec
                    })
                except Exception:
                    pass
    except Exception as e:
        print(f"⚠️ Advertencia al consultar centroides de categorías: {e}")

    result = ai_service.predict(image_bytes, description, category_centroids=centroids)

    if "error" in result and not result.get("predictions"):
        raise HTTPException(status_code=503, detail=result["error"])

    # Agregamos la ruta local de la imagen para el POST /api/reports
    result["image_path"] = f"/uploads/{filename}"
    return result


@app.post("/api/reports", response_model=schemas.ReportResponse)
def create_report(
    submission: schemas.ReportSubmission,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user) # Requiere login
):
    # Obtener category_id a partir del corrected_class o predicted_class
    final_class = submission.corrected_class if submission.corrected_class else submission.predicted_class
    
    # Manejo de categorías dinámicas
    if not submission.category_id:
        cat = crud.get_category_by_name(db, final_class)
        if not cat and submission.is_novel_category:
            # Crear categoría nueva en estado 'no verificada' con su centroide inicial
            cat = crud.create_or_get_novel_category(
                db=db,
                name=final_class,
                area=submission.suggested_area or "Infraestructura",
                description=submission.description,
                embedding=submission.embedding
            )
        if cat:
            submission.category_id = cat.id

    # Actualización en Caliente (Online Memory):
    # Auto-extraer embedding visual si no viene en el payload
    if not submission.embedding and submission.image_path:
        fname = os.path.basename(submission.image_path)
        img_full_path = os.path.join(UPLOADS_DIR, fname)
        if os.path.exists(img_full_path):
            try:
                with open(img_full_path, "rb") as f:
                    submission.embedding = ai_service.extract_pet_embedding(f.read())
            except Exception as err:
                print(f"⚠️ Error auto-extrayendo embedding: {err}")

    # Si la categoría ya existe y tenemos el embedding del reporte, actualizamos el centroide de forma ponderada
    if submission.category_id and submission.embedding:
        crud.update_category_centroid(db, submission.category_id, submission.embedding)

    # Crear reporte
    report = crud.create_report(
        db=db,
        report=submission,
        image_path=submission.image_path,
        user_id=current_user.id,
        is_novel_category=submission.is_novel_category or False,
        embedding=submission.embedding
    )
    
    # Crear prediccion vinculada
    model_version = crud.get_model_version(db)
    if model_version:
        ai_pred = schemas.AIPredictionBase(
            predicted_class=submission.predicted_class or "animal_reportado",
            confidence=submission.confidence or 1.0,
            model_version_id=model_version.id,
            is_novel_category=submission.is_novel_category,
        )
        saved_prediction = crud.create_ai_prediction(db, prediction=ai_pred, report_id=report.id)

        # Si el usuario corrigió la categoría en el frontend o es categoría novedosa, guardamos el feedback para active learning
        was_corrected = bool(submission.corrected_class and submission.corrected_class != submission.predicted_class)
        crud.create_or_update_feedback(
            db=db,
            prediction_id=saved_prediction.id,
            correct=not was_corrected,
            correct_class=submission.corrected_class if was_corrected else None,
            reviewer_id=current_user.id
        )
    
    # Refrescar para cargar las relationships
    db.refresh(report)
    return report

@app.get("/api/reports/{report_id}/matches", response_model=schemas.PetMatchResponse)
def get_report_matches(report_id: int, db: Session = Depends(database.get_db)):
    """Busca y rankea posibles coincidencias visuales y geográficas para una mascota."""
    target_report = crud.get_report(db, report_id)
    if not target_report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    
    matches = crud.find_candidate_pet_matches(db, target_report, top_k=6)
    return {
        "matches": matches,
        "total_checked": len(matches)
    }

@app.get("/api/alerts/active", response_model=List[schemas.ReportResponse])
def get_active_alerts(db: Session = Depends(database.get_db)):
    """Retorna los focos activos de cebos sospechosos y alertas críticas de envenenamiento."""
    return crud.get_active_danger_alerts(db)

@app.patch("/api/reports/{report_id}/resolve", response_model=schemas.ReportResponse)
def resolve_pet_report(
    report_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Marca una mascota como reunida con su familia o una alerta como neutralizada."""
    report = crud.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    report.is_resolved = True
    report.status = models.ReportStatus.RESUELTO
    db.commit()
    db.refresh(report)
    return report

@app.patch("/api/reports/{report_id}", response_model=schemas.ReportResponse)
def update_report_status(
    report_id: int,
    update: schemas.ReportUpdateStatus,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    report = crud.update_report(db, report_id, update.status, update.priority)
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    if update.is_resolved is not None:
        report.is_resolved = update.is_resolved
        db.commit()
    db.refresh(report)
    return report

@app.get("/api/reports", response_model=List[schemas.ReportResponse])
def get_reports(
    skip: int = 0,
    limit: int = 100,
    report_type: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Report)
    if report_type:
        query = query.filter(models.Report.report_type == report_type)
    return query.order_by(models.Report.created_at.desc()).offset(skip).limit(limit).all()


# --- FEEDBACK ---

@app.post("/api/predictions/{prediction_id}/feedback", response_model=schemas.FeedbackResponse)
def submit_feedback(
    prediction_id: int,
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Permite a un admin indicar si la predicción de la IA fue correcta o no.
    Si `correct=False`, debe indicar `correct_class` (la clase real).
    Este feedback se almacena y puede exportarse para reentrenamiento.
    """
    if not feedback.correct and not feedback.correct_class:
        raise HTTPException(status_code=400, detail="Debe indicar la clase correcta cuando la predicción es incorrecta.")
    
    prediction = db.query(models.AIPrediction).filter(models.AIPrediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Predicción no encontrada")

    fb = crud.create_or_update_feedback(
        db=db,
        prediction_id=prediction_id,
        correct=feedback.correct,
        correct_class=feedback.correct_class if not feedback.correct else None,
        reviewer_id=current_user.id
    )
    return fb


@app.get("/api/feedback/export")
def export_feedback_dataset(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Exporta los pares (imagen, clase_real) del feedback incorrecto para reentrenamiento.
    Solo incluye casos donde la IA se equivocó (correct=False).
    """
    feedbacks = crud.get_all_feedback(db)
    
    export = []
    for fb in feedbacks:
        if not fb.correct and fb.correct_class and fb.prediction and fb.prediction.report:
            report = fb.prediction.report
            export.append({
                "report_id": report.id,
                "image_path": report.image_path,
                "description": report.description,
                "predicted_class": fb.prediction.predicted_class,
                "correct_class": fb.correct_class,
                "confidence": fb.prediction.confidence,
                "reviewed_at": fb.created_at.isoformat() if fb.created_at else None,
            })
    
    return {
        "total_corrections": len(export),
        "data": export,
        "note": "Estos pares imagen+etiqueta pueden agregarse al dataset para reentrenamiento supervisado."
    }


# --- GESTIÓN DE CATEGORÍAS CANDIDATAS Y CONSOLIDACIÓN ---

@app.get("/api/admin/categories/pending")
def get_pending_categories(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Retorna categorías propuestas por la IA que esperan validación o consolidación
    por el equipo municipal, incluyendo el recuento de reportes agrupados en cada una.
    """
    pending = crud.get_pending_categories(db)
    results = []
    for cat in pending:
        count = db.query(models.Report).filter(models.Report.category_id == cat.id).count()
        results.append({
            "id": cat.id,
            "name": cat.name,
            "area": cat.area,
            "description": cat.description,
            "sample_count": cat.sample_count,
            "reports_count": count,
            "is_verified": cat.is_verified,
            "created_at": cat.created_at.isoformat() if cat.created_at else None,
        })
    return results


@app.post("/api/admin/categories/{category_id}/approve", response_model=schemas.CategoryResponse)
def approve_category(
    category_id: int,
    req: schemas.CategoryApproveRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Aprueba oficialmente una categoría propuesta por la IA."""
    cat = crud.approve_category(
        db,
        category_id=category_id,
        name=req.name,
        area=req.area,
        description=req.description
    )
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return cat


@app.post("/api/admin/categories/merge")
def merge_categories(
    req: schemas.CategoryMergeRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Fusiona dos categorías (ej: unifica 'crater' en 'bache').
    Reasigna los reportes y combina los centroides vectoriales.
    """
    target = crud.merge_categories(
        db,
        source_category_id=req.source_category_id,
        target_category_id=req.target_category_id,
        target_category_name=req.target_category_name
    )
    if not target:
        raise HTTPException(status_code=400, detail="Error fusionando categorías. Verifique los IDs o nombres.")
    return {
        "status": "ok",
        "message": f"Categoría fusionada exitosamente en '{target.name}'",
        "target_id": target.id,
        "new_sample_count": target.sample_count
    }


# --- REMUM ---

@app.get("/api/remum/mis-mascotas", response_model=List[schemas.RemumResponse])
def get_mis_mascotas(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.RemumRecord).filter(models.RemumRecord.user_id == current_user.id).order_by(models.RemumRecord.created_at.desc()).all()
@app.get("/api/remum/comunitarios", response_model=List[schemas.RemumResponse])
def get_comunitarios(db: Session = Depends(database.get_db)):
    return db.query(models.RemumRecord).filter(
        models.RemumRecord.is_community_pet == True,
        models.RemumRecord.latitude.isnot(None)
    ).all()

@app.post("/api/remum/", response_model=schemas.RemumResponse)
async def create_remum_record(
    pet_name: str = Form(...),
    pet_type: str = Form("perro"),
    pet_breed: Optional[str] = Form(None),
    color_description: Optional[str] = Form(None),
    chip_number: Optional[str] = Form(None),
    is_community_pet: bool = Form(False),
    address: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    image_path = None
    if file and file.filename:
        image_bytes = await file.read()
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOADS_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        image_path = f"/uploads/{filename}"

    remum_create = schemas.RemumCreate(
        pet_name=pet_name,
        pet_type=pet_type,
        pet_breed=pet_breed,
        color_description=color_description,
        chip_number=chip_number,
        is_community_pet=is_community_pet,
        address=address,
        latitude=latitude,
        longitude=longitude
    )
    return crud.create_remum_record(db, current_user.id, remum_create, image_path)

@app.post("/api/remum/{qr_code_id}/salud", response_model=schemas.HealthEventResponse)
def add_health_event(
    qr_code_id: str,
    event: schemas.HealthEventCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    remum = crud.get_remum_record_by_qr(db, qr_code_id)
    if not remum:
        raise HTTPException(status_code=404, detail="Credencial REMUM no encontrada")
    
    # Podriamos verificar si current_user es el dueño o admin, pero por la pregunta del PR lo dejamos abierto o condicionado.
    # Por ahora solo requerimos auth para evitar bots.
    return crud.add_health_event(db, remum.id, event)

@app.post("/api/remum/{qr_code_id}/padrinos", response_model=schemas.GodparentResponse)
def add_godparent(
    qr_code_id: str,
    godparent: schemas.GodparentCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    remum = crud.get_remum_record_by_qr(db, qr_code_id)
    if not remum:
        raise HTTPException(status_code=404, detail="Credencial REMUM no encontrada")
    if not remum.is_community_pet:
        raise HTTPException(status_code=400, detail="Esta mascota no es comunitaria, no se le pueden asignar padrinos.")
    
    return crud.add_godparent(db, remum.id, godparent)

@app.get("/api/remum/{qr_code_id}", response_model=schemas.RemumResponse)
def get_remum_record(
    qr_code_id: str,
    db: Session = Depends(database.get_db)
):
    remum = crud.get_remum_record_by_qr(db, qr_code_id)
    if not remum:
        raise HTTPException(status_code=404, detail="Credencial REMUM no encontrada")
    return remum

@app.post("/api/remum/{qr_code_id}/alerta", response_model=schemas.RemumResponse)
def trigger_remum_panic(
    qr_code_id: str,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    remum = crud.trigger_remum_panic(db, qr_code_id, lat=lat, lng=lng)
    if not remum:
        raise HTTPException(status_code=404, detail="Credencial REMUM no encontrada")
    if remum.user_id != current_user.id and current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="No tienes permiso para emitir alertas para esta mascota")
    return remum

@app.post("/api/remum/{qr_code_id}/padrinos", response_model=schemas.GodparentResponse)
def add_godparent(
    qr_code_id: str,
    godparent: schemas.GodparentCreate,
    db: Session = Depends(database.get_db)
):
    remum = crud.get_remum_record_by_qr(db, qr_code_id)
    if not remum:
        raise HTTPException(status_code=404, detail="Credencial REMUM no encontrada")
    if not remum.is_community_pet:
        raise HTTPException(status_code=400, detail="Esta mascota no es comunitaria, no admite padrinos")
    
    return crud.add_godparent(db, remum.id, godparent)

