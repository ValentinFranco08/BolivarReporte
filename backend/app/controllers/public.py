from fastapi import APIRouter, Depends
from .. import schemas
from ..dependencies import get_predictor, get_category_service

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Reporte Bolívar API v2.0 — Multimodal"}

@router.get("/api/health")
def health_check(model=Depends(get_predictor)):
    return {"status": "ok", "model_ready": model.ready,
            "model_version": model.model_version if model.ready else None}

@router.get("/api/categories", response_model=list[schemas.CategoryResponse])
def get_categories(service=Depends(get_category_service)):
    return service.list()
