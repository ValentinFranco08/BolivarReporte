import json
import logging
from ml.inference.contracts import Predictor
from ..infrastructure.storage import FileStorage
from ..core.errors import ApplicationError, ServiceUnavailableError

logger = logging.getLogger(__name__)

class ClassificationService:
    def __init__(self, predictor: Predictor, categories, storage: FileStorage):
        self.predictor = predictor
        self.categories = categories
        self.storage = storage

    def classify(self, image: bytes, text: str, content_type: str | None):
        if not (content_type or "").startswith("image/"):
            raise ApplicationError("El archivo debe ser una imagen.")
        centroids = []
        for category in self.categories.list():
            if not category.embedding_centroid:
                continue
            try:
                vector = json.loads(category.embedding_centroid)
            except (ValueError, TypeError):
                logger.warning("Centroide inválido en categoría %s", category.id)
                continue
            centroids.append({"id": category.id, "name": category.name,
                              "area": category.area, "centroid": vector})
        result = self.predictor.predict(image, (text or "").strip(), category_centroids=centroids)
        if "error" in result and not result.get("predictions"):
            raise ServiceUnavailableError(result["error"])
        result["image_path"] = self.storage.save(image)
        return result

    def embedding_from_path(self, image_path):
        try:
            return self.predictor.extract_pet_embedding(self.storage.read(image_path))
        except FileNotFoundError:
            return None
