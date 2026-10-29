from .base import Repository
from ..models import Report, AnimalReportType

class ReportRepository(Repository[Report]):
    def __init__(self, session):
        super().__init__(session, Report)

    def list(self, skip=0, limit=100, report_type=None):
        query = self.session.query(Report)
        if report_type:
            query = query.filter(Report.report_type == report_type)
        return query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

    def active_alerts(self):
        return self.session.query(Report).filter(
            Report.report_type == AnimalReportType.ALERTA_CEBO,
            Report.is_resolved.is_(False)
        ).order_by(Report.created_at.desc()).all()

    def matching_candidates(self, target, opposite_types):
        return self.session.query(Report).filter(
            Report.id != target.id, Report.report_type.in_(opposite_types),
            Report.pet_type == target.pet_type, Report.is_resolved.is_(False),
            Report.embedding.isnot(None)
        ).all()

    def reassign_category(self, source_id, target_id):
        self.session.query(Report).filter(Report.category_id == source_id).update(
            {Report.category_id: target_id}, synchronize_session="fetch"
        )

    def with_images(self):
        return self.session.query(Report).filter(Report.image_path.isnot(None)).all()
