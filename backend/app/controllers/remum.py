from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form
from .. import schemas, auth
from ..dependencies import get_remum_service

router = APIRouter()

@router.get("/api/remum/mis-mascotas", response_model=list[schemas.RemumResponse])
def get_mis_mascotas(service=Depends(get_remum_service), current_user=Depends(auth.get_current_user_optional)):
    return service.by_owner(current_user)

@router.get("/api/remum/comunitarios", response_model=list[schemas.RemumResponse])
def get_comunitarios(service=Depends(get_remum_service)):
    return service.community()

@router.post("/api/remum/", response_model=schemas.RemumResponse)
async def create_remum_record(
    pet_name: str = Form(...), pet_type: str = Form("perro"),
    pet_breed: Optional[str] = Form(None), color_description: Optional[str] = Form(None),
    chip_number: Optional[str] = Form(None), is_community_pet: bool = Form(False),
    address: Optional[str] = Form(None), latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None), file: UploadFile = File(None),
    service=Depends(get_remum_service), current_user=Depends(auth.get_current_user_optional),
):
    data = schemas.RemumCreate(pet_name=pet_name, pet_type=pet_type, pet_breed=pet_breed,
        color_description=color_description, chip_number=chip_number,
        is_community_pet=is_community_pet, address=address, latitude=latitude, longitude=longitude)
    image = await file.read() if file and file.filename else None
    from starlette.concurrency import run_in_threadpool
    return await run_in_threadpool(service.create, data, current_user, image,
                                    file.filename if file and file.filename else "image.jpg")

@router.post("/api/remum/{qr_code_id}/salud", response_model=schemas.HealthEventResponse)
def add_health_event(qr_code_id: str, event: schemas.HealthEventCreate,
                     service=Depends(get_remum_service), current_user=Depends(auth.get_current_user)):
    return service.add_health_event(qr_code_id, event)

@router.post("/api/remum/{qr_code_id}/padrinos", response_model=schemas.GodparentResponse)
def add_godparent(qr_code_id: str, godparent: schemas.GodparentCreate,
                 service=Depends(get_remum_service), current_user=Depends(auth.get_current_user)):
    return service.add_godparent(qr_code_id, godparent)

@router.get("/api/remum/{qr_code_id}", response_model=schemas.RemumResponse)
def get_remum_record(qr_code_id: str, service=Depends(get_remum_service)):
    return service.get(qr_code_id)

@router.post("/api/remum/{qr_code_id}/alerta", response_model=schemas.RemumResponse)
def trigger_remum_panic(qr_code_id: str, lat: Optional[float] = None, lng: Optional[float] = None,
                        service=Depends(get_remum_service), current_user=Depends(auth.get_current_user)):
    return service.panic(qr_code_id, current_user, lat, lng)
