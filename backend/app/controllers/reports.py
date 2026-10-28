from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form
from .. import schemas, auth
from ..dependencies import get_report_service, get_matching_service, get_classification_service

router = APIRouter()

@router.post("/api/ai/predict")
async def predict(file: UploadFile = File(...), text: str = Form(default=""),
                  service=Depends(get_classification_service)):
    # El cálculo CPU/GPU se ejecuta fuera del event loop HTTP.
    from starlette.concurrency import run_in_threadpool
    return await run_in_threadpool(service.classify, await file.read(), text, file.content_type)

@router.post("/api/reports", response_model=schemas.ReportResponse)
def create_report(submission: schemas.ReportSubmission, service=Depends(get_report_service),
                  current_user=Depends(auth.get_current_user_optional)):
    return service.create(submission, current_user)

@router.get("/api/reports/{report_id}/matches", response_model=schemas.PetMatchResponse)
def get_report_matches(report_id: int, service=Depends(get_report_service),
                       matching=Depends(get_matching_service)):
    matches = matching.find(service.get(report_id), top_k=6)
    return {"matches": matches, "total_checked": len(matches)}

@router.get("/api/alerts/active", response_model=list[schemas.ReportResponse])
def get_active_alerts(service=Depends(get_report_service)):
    return service.active_alerts()

@router.patch("/api/reports/{report_id}/resolve", response_model=schemas.ReportResponse)
def resolve_pet_report(report_id: int, service=Depends(get_report_service),
                       current_user=Depends(auth.get_current_user)):
    return service.resolve(report_id)

@router.patch("/api/reports/{report_id}", response_model=schemas.ReportResponse)
def update_report_status(report_id: int, update: schemas.ReportUpdateStatus,
                         service=Depends(get_report_service), current_user=Depends(auth.get_current_user)):
    return service.update(report_id, update)

@router.get("/api/reports", response_model=list[schemas.ReportResponse])
def get_reports(skip: int = 0, limit: int = 100, report_type: Optional[str] = None,
                service=Depends(get_report_service)):
    return service.list(skip, limit, report_type)
