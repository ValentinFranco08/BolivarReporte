import json
import numpy as np
from ..core.errors import ApplicationError, NotFoundError
from ..models import Category

class CentroidPolicy:
    """Media ponderada normalizada, con validación dimensional."""
    @staticmethod
    def combine(first, first_count, second, second_count=1):
        left, right = np.asarray(first, dtype=float), np.asarray(second, dtype=float)
        if left.ndim != 1 or left.shape != right.shape or not left.size:
            raise ApplicationError("Los embeddings deben tener la misma dimensión")
        vector = first_count * left + second_count * right
        if not np.isfinite(vector).all():
            raise ApplicationError("El embedding contiene valores no finitos")
        return (vector / (np.linalg.norm(vector) or 1.0)).tolist()

class CategoryService:
    def __init__(self, categories, reports, unit_of_work=None):
        self.categories = categories
        self.reports = reports
        self.unit_of_work = unit_of_work

    def create_or_get(self, name, area, description=None, embedding=None):
        existing = self.categories.by_name(name)
        if existing:
            return existing
        centroid = CentroidPolicy.combine(embedding, 0, embedding) if embedding else None
        return self.categories.add(Category(
            name=name, area=area, description=description, is_verified=False,
            embedding_centroid=json.dumps(centroid) if centroid else None,
            sample_count=1, active=True,
        ))

    def update_centroid(self, category_id, embedding):
        category = self.categories.get(category_id)
        if category is None:
            return None
        old = json.loads(category.embedding_centroid) if category.embedding_centroid else embedding
        count = (category.sample_count or 1) if category.embedding_centroid else 0
        category.embedding_centroid = json.dumps(CentroidPolicy.combine(old, count, embedding))
        category.sample_count = count + 1
        return category

    def approve(self, category_id, name=None, area=None, description=None):
        category = self.categories.get(category_id)
        if category is None:
            return None
        category.is_verified = True
        for field, value in {"name": name, "area": area, "description": description}.items():
            if value:
                setattr(category, field, value)
        return category

    def merge(self, source_category_id, target_category_id=None, target_category_name=None):
        source = self.categories.get(source_category_id)
        target = (self.categories.get(target_category_id) if target_category_id
                  else self.categories.by_name(target_category_name))
        if source is None or target is None:
            return None
        if source.id == target.id:
            raise ApplicationError("No se puede fusionar una categoría consigo misma")
        if source.embedding_centroid and target.embedding_centroid:
            target.embedding_centroid = json.dumps(CentroidPolicy.combine(
                json.loads(source.embedding_centroid), source.sample_count or 1,
                json.loads(target.embedding_centroid), target.sample_count or 1,
            ))
            target.sample_count = (source.sample_count or 1) + (target.sample_count or 1)
        self.reports.reassign_category(source.id, target.id)
        source.active = False
        return target

    def pending(self):
        return [{"id": cat.id, "name": cat.name, "area": cat.area,
                 "description": cat.description, "sample_count": cat.sample_count,
                 "reports_count": count, "is_verified": cat.is_verified,
                 "created_at": cat.created_at.isoformat() if cat.created_at else None}
                for cat, count in self.categories.pending_with_counts()]

    def list(self, only_verified=False):
        return self.categories.list(only_verified)

    def get(self, category_id):
        return self.categories.get(category_id)

    def by_name(self, name):
        return self.categories.by_name(name)

    def approve_checked(self, category_id, request):
        with self.unit_of_work:
            category = self.approve(category_id, **request.model_dump())
            if category is None:
                raise NotFoundError("Categoría no encontrada")
        return category

    def merge_checked(self, request):
        with self.unit_of_work:
            target = self.merge(**request.model_dump())
            if target is None:
                raise ApplicationError("Error fusionando categorías. Verifique los IDs o nombres.")
        return {"status": "ok", "message": f"Categoría fusionada exitosamente en '{target.name}'",
                "target_id": target.id, "new_sample_count": target.sample_count}
