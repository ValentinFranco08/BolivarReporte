from .base import Repository
from ..models import RemumRecord

class RemumRepository(Repository[RemumRecord]):
    def __init__(self, session):
        super().__init__(session, RemumRecord)

    def by_qr(self, qr_code_id):
        return self.session.query(RemumRecord).filter(RemumRecord.qr_code_id == qr_code_id).first()

    def by_owner(self, user_id):
        return self.session.query(RemumRecord).filter(RemumRecord.user_id == user_id).order_by(
            RemumRecord.created_at.desc()
        ).all()

    def community(self):
        return self.session.query(RemumRecord).filter(
            RemumRecord.is_community_pet.is_(True), RemumRecord.latitude.isnot(None)
        ).all()

    def add_related(self, entity):
        self.session.add(entity)
        self.session.flush()
        return entity
