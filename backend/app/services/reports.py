import json
from .. import models
from ..core.errors import NotFoundError
from ..repositories.reports import ReportStore

class ReportService:
    def __init__(self, reports: ReportStore, categories, users, predictions, feedback,
                 classification, unit_of_work):
        self.reports = reports
        self.categories = categories
        self.users = users
        self.predictions = predictions
        self.feedback = feedback
        self.classification = classification
        self.unit_of_work = unit_of_work

    def get(self, report_id):
        report = self.reports.get(report_id)
        if report is None:
            raise NotFoundError("Reporte no encontrado")
        return report

    def create(self, submission, current_user=None):
        data = submission.model_copy(deep=True)
        with self.unit_of_work:
            final_class = data.corrected_class or data.predicted_class
            category = self.categories.get(data.category_id) if data.category_id else self.categories.by_name(final_class)
            if not data.embedding and data.image_path:
                data.embedding = self.classification.embedding_from_path(data.image_path)
            created_category = category is None and data.is_novel_category
            if created_category:
                category = self.categories.create_or_get(
                    final_class, data.suggested_area or "Infraestructura", data.description, data.embedding
                )
            if category is not None:
                data.category_id = category.id
                if data.embedding and not created_category:
                    self.categories.update_centroid(category.id, data.embedding)
            user = current_user or self.users.default_citizen()
            user_id = user.id if user else None
            report = self.create_record(data, data.image_path, user_id,
                                        bool(data.is_novel_category), data.embedding)
            version = self.predictions.model_version()
            if version:
                prediction = self.predictions.add(models.AIPrediction(
                    report_id=report.id, model_version_id=version.id,
                    predicted_class=data.predicted_class or "animal_reportado",
                    confidence=data.confidence if data.confidence is not None else 1.0,
                ))
                corrected = bool(data.corrected_class and data.corrected_class != data.predicted_class)
                self.feedback.save(prediction.id, not corrected,
                                   data.corrected_class if corrected else None, user_id)
        return report

    def create_record(self, data, image_path, user_id=None, is_novel_category=False, embedding=None):
        fields = data.model_dump(include=set(models.Report.__table__.columns.keys()))
        fields.update(image_path=image_path, user_id=user_id,
                      is_novel_category=is_novel_category,
                      embedding=json.dumps(embedding) if embedding else None)
        return self.reports.add(models.Report(**fields))

    def resolve(self, report_id):
        with self.unit_of_work:
            report = self.get(report_id)
            report.is_resolved = True
            report.status = models.ReportStatus.RESUELTO
        return report

    def update(self, report_id, update):
        with self.unit_of_work:
            report = self.get(report_id)
            for field, value in update.model_dump(exclude_none=True).items():
                setattr(report, field, value)
        return report

    def list(self, skip=0, limit=100, report_type=None):
        return self.reports.list(skip, limit, report_type)

    def active_alerts(self):
        return self.reports.active_alerts()
