from fastapi import APIRouter, Depends
from .. import schemas, auth
from ..dependencies import get_feedback_service

router = APIRouter()

@router.post("/api/predictions/{prediction_id}/feedback", response_model=schemas.FeedbackResponse)
def submit_feedback(prediction_id: int, feedback: schemas.FeedbackCreate,
                    service=Depends(get_feedback_service), current_user=Depends(auth.get_current_user)):
    return service.submit(prediction_id, feedback, current_user.id)

@router.get("/api/feedback/export")
def export_feedback_dataset(service=Depends(get_feedback_service), current_user=Depends(auth.get_current_user)):
    return service.export()
