"""Casos de uso de registro y acceso; independientes de FastAPI."""
from datetime import timedelta
from .. import models
from ..core.errors import ApplicationError
from ..infrastructure.security import (
    get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES,
)


class AuthService:
    def __init__(self, users, unit_of_work):
        self.users = users
        self.unit_of_work = unit_of_work

    def register(self, data):
        if self.users.by_email(data.email):
            raise ApplicationError("El email ya está registrado")
        with self.unit_of_work:
            user = self.users.add(models.User(
                name=data.name, email=data.email, password_hash=get_password_hash(data.password),
            ))
        return user

    def login(self, email, password):
        user = self.users.by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise ApplicationError("Email o contraseña incorrectos")
        token = create_access_token(
            data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return {"access_token": token, "token_type": "bearer"}
