"""Contraseñas y tokens JWT; estas funciones no dependen del transporte HTTP."""
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = "super-secret-key-bolivar-responde"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
_passwords = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return _passwords.verify(plain_password, hashed_password)


def get_password_hash(password):
    return _passwords.hash(password)


def create_access_token(data, expires_delta=None):
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def token_email(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
