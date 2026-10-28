import json
import logging
from ..models import AnimalReportType
from .similarity import (calculate_cosine_similarity, calculate_semantic_similarity,
                         calculate_pet_match_score, haversine_km)

logger = logging.getLogger(__name__)

class MatchingPolicy:
    OPPOSITE_TYPES = {
        "perdido": (AnimalReportType.ENCONTRADO, AnimalReportType.EN_TRANSITO),
        "encontrado": (AnimalReportType.PERDIDO,),
        "en_transito": (AnimalReportType.PERDIDO,),
    }

    def opposite_types(self, report_type):
        return self.OPPOSITE_TYPES.get(report_type,
            (AnimalReportType.PERDIDO, AnimalReportType.ENCONTRADO))

    def score(self, target, candidate, embedding):
        visual = calculate_cosine_similarity(embedding, json.loads(candidate.embedding))
        distance = haversine_km(target.latitude, target.longitude, candidate.latitude, candidate.longitude)
        semantic = calculate_semantic_similarity(target.color_description, target.pet_breed,
            target.description, candidate.color_description, candidate.pet_breed, candidate.description)
        combined = calculate_pet_match_score(visual, distance, semantic_sim=semantic)
        return {"report": candidate, "visual_similarity": round(visual, 3),
                "semantic_similarity": round(semantic, 3), "distance_km": distance,
                "combined_score": combined}

    def accepts(self, score):
        return (score["visual_similarity"] >= .20 or score["combined_score"] >= .35
                or (score["semantic_similarity"] >= .70 and score["combined_score"] >= .30))

class MatchingService:
    def __init__(self, reports, policy=None):
        self.reports = reports
        self.policy = policy or MatchingPolicy()

    def find(self, target, top_k=5):
        if not target.embedding:
            return []
        try:
            embedding = json.loads(target.embedding)
        except (ValueError, TypeError):
            return []
        candidates = self.reports.matching_candidates(target, self.policy.opposite_types(target.report_type))
        scored = []
        for candidate in candidates:
            try:
                score = self.policy.score(target, candidate, embedding)
            except (ValueError, TypeError):
                logger.warning("Embedding inválido en reporte %s", candidate.id)
                continue
            if self.policy.accepts(score):
                scored.append(score)
        return sorted(scored, key=lambda item: item["combined_score"], reverse=True)[:top_k]
