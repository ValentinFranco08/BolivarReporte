"""Crear, consultar y actualizar reportes; una transacción por operación completa."""
import json
from .. import models, schemas
from ..core.errors import NotFoundError


class ReportService:
    def __init__(self, reports, categories, users, predictions, feedback,
                 classification, unit_of_work):
        self.reports = reports
        self.categories = categories
        self.users = users
        self.predictions = predictions
        self.feedback = feedback
        self.classification = classification
        self.unit_of_work = unit_of_work

    def create(self, submission, current_user=None):
        """Preparar datos, guardar el reporte y registrar la predicción juntos."""
        data = submission.model_copy(deep=True)
        with self.unit_of_work:
            # 1. Completar el embedding y resolver la categoría definitiva.
            if not data.embedding and data.image_path:
                data.embedding = self.classification.embedding_from_path(data.image_path)
            data.category_id = self.categories.resolve_for_report(data)

            # 2. Vincular al usuario y persistir solamente los campos del reporte.
            user = current_user or self.users.default_citizen()
            user_id = user.id if user else None
            fields = data.model_dump(include=set(schemas.ReportCreate.model_fields))
            report = self.reports.add(models.Report(
                **fields, image_path=data.image_path, user_id=user_id,
                is_novel_category=bool(data.is_novel_category),
                embedding=json.dumps(data.embedding) if data.embedding else None,
            ))

            # 3. Vincular predicción y corrección antes de confirmar la transacción.
            self._record_prediction(report.id, data, user_id)
        return report

    def _record_prediction(self, report_id, data, reviewer_id):
        version = self.predictions.model_version()
        if version is None:
            return
        prediction = self.predictions.add(models.AIPrediction(
            report_id=report_id, model_version_id=version.id,
            predicted_class=data.predicted_class or "animal_reportado",
            confidence=data.confidence if data.confidence is not None else 1.0,
        ))
        corrected = bool(data.corrected_class and data.corrected_class != data.predicted_class)
        self.feedback.upsert(
            prediction.id, correct=not corrected,
            correct_class=data.corrected_class if corrected else None, reviewer_id=reviewer_id,
        )

    def get(self, report_id):
        report = self.reports.get(report_id)
        if report is None:
            raise NotFoundError("Reporte no encontrado")
        return report

    def list(self, skip=0, limit=100, report_type=None):
        return self.reports.list(skip, limit, report_type)

    def active_alerts(self):
        return self.reports.active_alerts()

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
