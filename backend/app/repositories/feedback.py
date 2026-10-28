from .base import Repository
from ..models import Feedback, AIPrediction, Report

class FeedbackRepository(Repository[Feedback]):
    def __init__(self, session):
        super().__init__(session, Feedback)

    def by_prediction(self, prediction_id):
        return self.session.query(Feedback).filter(Feedback.prediction_id == prediction_id).first()

    def list(self, pending_only=False):
        query = self.session.query(Feedback).join(AIPrediction).join(Report)
        if pending_only:
            query = query.filter(Feedback.used_for_retraining.is_(False))
        return query.all()

    def mark_retrained(self, ids):
        self.session.query(Feedback).filter(Feedback.id.in_(ids)).update(
            {Feedback.used_for_retraining: True}, synchronize_session="fetch"
        )
