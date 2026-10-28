from sqlalchemy import func
from .base import Repository
from ..models import Category, Report

class CategoryRepository(Repository[Category]):
    def __init__(self, session):
        super().__init__(session, Category)

    def list(self, only_verified=False):
        query = self.session.query(Category).filter(Category.active.is_(True))
        if only_verified:
            query = query.filter(Category.is_verified.is_(True))
        return query.all()

    def by_name(self, name):
        return self.session.query(Category).filter(Category.name == name).first()

    def pending(self):
        return self.session.query(Category).filter(
            Category.active.is_(True), Category.is_verified.is_(False)
        ).order_by(Category.created_at.desc()).all()

    def pending_with_counts(self):
        return self.session.query(Category, func.count(Report.id)).outerjoin(
            Report, Report.category_id == Category.id
        ).filter(Category.active.is_(True), Category.is_verified.is_(False)).group_by(
            Category.id
        ).order_by(Category.created_at.desc()).all()
