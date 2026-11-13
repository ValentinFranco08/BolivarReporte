"""Cálculos puros de similitud visual, semántica y geográfica."""
import math
import re
from typing import Optional
import numpy as np

def haversine_km(lat1: Optional[float], lon1: Optional[float], lat2: Optional[float], lon2: Optional[float]) -> float:
    """Calcula la distancia geodésica en kilómetros entre dos coordenadas."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 999.0
    R = 6371.0  # Radio medio de la Tierra en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def calculate_cosine_similarity(vec1: list, vec2: list) -> float:
    """Calcula la similitud coseno entre dos vectores normalizados y la calibra para percepción humana."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = np.dot(vec1, vec2)
    raw_sim = float(dot)
    
    # Los embeddings visuales de ViT multi-escala para animales no relacionados o de raza muy distinta rondan <= 0.25.
    # Animales con rasgos o coloración similar, o distinta postura rondan 0.35 a 0.65.
    # Mismo animal con foto idéntica o muy cercana ronda 0.75 a 1.00.
    # Calibramos la proyección continua [0.25, 0.85] -> [0.0, 1.0].
    if raw_sim <= 0.25:
        return 0.0
    scaled = (raw_sim - 0.25) / (0.85 - 0.25)
    return round(min(1.0, max(0.0, scaled)), 3)

def normalize_text_tokens(text: Optional[str]) -> set:
    if not text:
        return set()
    cleaned = re.sub(r'[^a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s]', ' ', text.lower())
    STOPWORDS = {"de", "y", "en", "con", "el", "la", "los", "las", "un", "una", "por", "al", "del", "se", "es"}
    return {w for w in cleaned.split() if len(w) > 2 and w not in STOPWORDS}

def calculate_semantic_similarity(
    target_color: Optional[str],
    target_breed: Optional[str],
    target_desc: Optional[str],
    cand_color: Optional[str],
    cand_breed: Optional[str],
    cand_desc: Optional[str]
) -> float:
    """Promedia únicamente las señas que se pueden comparar en ambos reportes."""
    values = []
    for weight, first, second in (
        (0.50, target_color, cand_color),
        (0.35, target_breed, cand_breed),
        (0.15, target_desc, cand_desc),
    ):
        a, b = normalize_text_tokens(first), normalize_text_tokens(second)
        if a and b:
            values.append((weight, len(a & b) / len(a | b)))
    if not values:
        return None
    return round(sum(w * score for w, score in values) / sum(w for w, _ in values), 3)


def calculate_pet_match_score(
    visual_sim: float,
    distance_km: float,
    semantic_sim: Optional[float] = 0.5,
    max_radius_km: float = 5.0
) -> float:
    """
    Score combinado multimodal:
    - 65% Similitud visual profunda (Vision Transformer multi-escala con auto-crop).
    - 20% Rasgos semánticos (Pelaje, raza y señas particulares).
    - 15% Factor de cercanía geográfica en el partido de Bolívar.
    """
    norm_vis = max(0.0, min(1.0, visual_sim))
    norm_sem = max(0.0, min(1.0, semantic_sim or 0.0))
    geo_factor = max(0.0, 1.0 - (distance_km / max_radius_km)) if distance_km <= max_radius_km else 0.0
    
    combined = (0.65 * norm_vis) + (0.20 * norm_sem) + (0.15 * geo_factor)
    return round(combined, 3)


