"""Dependencias HTTP de autenticación: obtener el usuario a partir de su token."""
from typing import Optional
from jose import JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import database, models
from .infrastructure.security import token_email
from .repositories.users import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)


def _user_from_token(token, db):
    if not token:
        return None
    try:
        email = token_email(token)
    except JWTError:
        return None
    if not isinstance(email, str) or not email:
        return None
    return UserRepository(db).by_email(email)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    user = _user_from_token(token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme_optional),
                              db: Session = Depends(database.get_db)) -> Optional[models.User]:
    return _user_from_token(token, db)
