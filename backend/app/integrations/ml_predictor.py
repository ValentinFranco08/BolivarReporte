"""Carga diferida: importar la API no carga pesos ni descarga modelos."""
from threading import RLock

class LazyPredictor:
    def __init__(self, factory=None, pet_checkpoint=None):
        self._factory = factory
        self._pet_checkpoint = pet_checkpoint
        self._pet_predictor = None
        self._instance = None
        self._lock = RLock()

    def initialize(self):
        with self._lock:
            if self._instance is None:
                factory = self._factory
                if factory is None:
                    from ml.inference.predictor import MultimodalPredictor
                    factory = MultimodalPredictor
                self._instance = factory()
            return self._instance

    @property
    def ready(self):
        return self._instance is not None and self._instance.ready

    @property
    def model_version(self):
        return self._instance.model_version if self._instance else "multimodal-v1"

    def predict(self, image_bytes, text, category_centroids=None):
        with self._lock:
            return self.initialize().predict(image_bytes, text, category_centroids)

    def extract_pet_embedding(self, image_bytes):
        with self._lock:
            return self.initialize().extract_pet_embedding(image_bytes)

    @property
    def pet_reid_enabled(self):
        return bool(self._pet_checkpoint)

    def pet_identity_embedding(self, image_bytes):
        with self._lock:
            if self._pet_predictor is None:
                from ml.inference.pet_predictor import PetPredictor
                self._pet_predictor = PetPredictor(self._pet_checkpoint)
            return self._pet_predictor.embed(image_bytes)

    def extract_embedding(self, image_bytes, text):
        with self._lock:
            return self.initialize().extract_embedding(image_bytes, text)
