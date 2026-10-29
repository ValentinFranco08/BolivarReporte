import json
import numpy as np
from ..core.errors import ApplicationError, NotFoundError
from ..models import Category

def combine_centroids(first, first_count, second, second_count=1):
    left, right = np.asarray(first, dtype=float), np.asarray(second, dtype=float)
    if left.ndim != 1 or left.shape != right.shape or not left.size:
        raise ApplicationError("Los embeddings deben tener la misma dimensión")
    vector = first_count * left + second_count * right
    if not np.isfinite(vector).all():
        raise ApplicationError("El embedding contiene valores no finitos")
    return (vector / (np.linalg.norm(vector) or 1.0)).tolist()


class CategoryService:
    def __init__(self, categories, reports, unit_of_work):
        self.categories = categories
        self.reports = reports
        self.unit_of_work = unit_of_work

    def create_or_get(self, name, area, description=None, embedding=None):
        """Participa de la transacción del reporte; no confirma por separado."""
        existing = self.categories.by_name(name)
        if existing:
            return existing
        centroid = combine_centroids(embedding, 0, embedding) if embedding else None
        return self.categories.add(Category(
            name=name, area=area, description=description, is_verified=False,
            embedding_centroid=json.dumps(centroid) if centroid else None,
            sample_count=1, active=True,
        ))

    def update_centroid(self, category_id, embedding):
        """Modificar el centroide dentro de la transacción del caso de uso."""
        category = self.categories.get(category_id)
        if category is None:
            return None
        old = json.loads(category.embedding_centroid) if category.embedding_centroid else embedding
        count = (category.sample_count or 1) if category.embedding_centroid else 0
        category.embedding_centroid = json.dumps(combine_centroids(old, count, embedding))
        category.sample_count = count + 1
        return category

    def resolve_for_report(self, submission):
        """Asignar categoría y actualizar su centroide dentro de la transacción del reporte."""
        final_class = submission.corrected_class or submission.predicted_class
        category = (self.categories.get(submission.category_id) if submission.category_id
                    else self.categories.by_name(final_class))
        created = category is None and submission.is_novel_category
        if created:
            category = self.create_or_get(
                final_class, submission.suggested_area or "Infraestructura",
                submission.description, submission.embedding,
            )
        if category is None:
            return submission.category_id
        if submission.embedding and not created:
            self.update_centroid(category.id, submission.embedding)
        return category.id

    def approve(self, category_id, request):
        with self.unit_of_work:
            category = self.categories.get(category_id)
            if category is None:
                raise NotFoundError("Categoría no encontrada")
            category.is_verified = True
            for field, value in request.model_dump().items():
                if value:
                    setattr(category, field, value)
        return category

    def merge(self, request):
        with self.unit_of_work:
            source = self.categories.get(request.source_category_id)
            target = (self.categories.get(request.target_category_id) if request.target_category_id
                      else self.categories.by_name(request.target_category_name))
            if source is None or target is None:
                raise ApplicationError("Error fusionando categorías. Verifique los IDs o nombres.")
            if source.id == target.id:
                raise ApplicationError("No se puede fusionar una categoría consigo misma")
            if source.embedding_centroid and target.embedding_centroid:
                target.embedding_centroid = json.dumps(combine_centroids(
                    json.loads(source.embedding_centroid), source.sample_count or 1,
                    json.loads(target.embedding_centroid), target.sample_count or 1,
                ))
                target.sample_count = (source.sample_count or 1) + (target.sample_count or 1)
            self.reports.reassign_category(source.id, target.id)
            source.active = False
        return {"status": "ok", "message": f"Categoría fusionada exitosamente en '{target.name}'",
                "target_id": target.id, "new_sample_count": target.sample_count}

    def pending(self):
        return [{"id": cat.id, "name": cat.name, "area": cat.area,
                 "description": cat.description, "sample_count": cat.sample_count,
                 "reports_count": count, "is_verified": cat.is_verified,
                 "created_at": cat.created_at.isoformat() if cat.created_at else None}
                for cat, count in self.categories.pending_with_counts()]

    def list(self, only_verified=False):
        return self.categories.list(only_verified)
