from datetime import timedelta
from .. import models
from ..core.errors import ApplicationError

class AuthService:
    def __init__(self, users, passwords, tokens, unit_of_work):
        self.users = users
        self.passwords = passwords
        self.tokens = tokens
        self.unit_of_work = unit_of_work

    def register(self, data):
        if self.users.by_email(data.email):
            raise ApplicationError("El email ya está registrado")
        with self.unit_of_work:
            user = self.users.add(models.User(name=data.name, email=data.email,
                password_hash=self.passwords.get_password_hash(data.password)))
        return user

    def login(self, email, password):
        user = self.users.by_email(email)
        if user is None or not self.passwords.verify_password(password, user.password_hash):
            raise ApplicationError("Email o contraseña incorrectos")
        token = self.tokens.create_access_token(data={"sub": user.email},
            expires_delta=timedelta(minutes=self.tokens.ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": token, "token_type": "bearer"}
