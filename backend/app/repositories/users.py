from .base import Repository
from ..models import User, UserRole

class UserRepository(Repository[User]):
    def __init__(self, session):
        super().__init__(session, User)

    def by_email(self, email):
        return self.session.query(User).filter(User.email == email).first()

    def default_citizen(self):
        return self.session.query(User).filter(User.role == UserRole.CITIZEN).first()
