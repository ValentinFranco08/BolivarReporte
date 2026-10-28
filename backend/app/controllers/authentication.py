from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from .. import schemas, auth
from ..dependencies import get_auth_service

router = APIRouter()

@router.post("/api/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, service=Depends(get_auth_service)):
    return service.register(user)

@router.post("/api/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), service=Depends(get_auth_service)):
    return service.login(form_data.username, form_data.password)

@router.get("/api/auth/me", response_model=schemas.UserResponse)
def read_users_me(current_user=Depends(auth.get_current_user)):
    return current_user
