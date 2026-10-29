from fastapi import APIRouter, Depends
from .. import schemas, auth
from ..dependencies import get_category_service

router = APIRouter()

@router.get("/api/admin/categories/pending")
def get_pending_categories(service=Depends(get_category_service), current_user=Depends(auth.get_current_user)):
    return service.pending()

@router.post("/api/admin/categories/{category_id}/approve", response_model=schemas.CategoryResponse)
def approve_category(category_id: int, req: schemas.CategoryApproveRequest,
                     service=Depends(get_category_service), current_user=Depends(auth.get_current_user)):
    return service.approve(category_id, req)

@router.post("/api/admin/categories/merge")
def merge_categories(req: schemas.CategoryMergeRequest, service=Depends(get_category_service),
                     current_user=Depends(auth.get_current_user)):
    return service.merge(req)
