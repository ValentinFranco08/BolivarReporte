"""Fachada compatible para scripts anteriores; la implementación reside en ml/."""
from .infrastructure.predictor import predictor as ai_service
from .services.similarity import (
    haversine_km, calculate_cosine_similarity, calculate_pet_match_score,
    calculate_semantic_similarity, normalize_text_tokens,
)

def smart_animal_crop(image):
    from ml.preprocessing.images import smart_animal_crop as crop
    return crop(image)
