from .base import Repository
from ..models import AIPrediction, ModelVersion

class PredictionRepository(Repository[AIPrediction]):
    def __init__(self, session):
        super().__init__(session, AIPrediction)

    def model_version(self, name="multimodal-v1"):
        return self.session.query(ModelVersion).filter(ModelVersion.name == name).first()

    def add_version(self, version):
        self.session.add(version)
        self.session.flush()
        return version
