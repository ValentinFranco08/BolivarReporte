import json
import logging
import numpy as np
from ..models import AnimalReportType
from .coat_color import incompatible_coat_colors
from .similarity import (calculate_cosine_similarity, calculate_semantic_similarity,
                         calculate_pet_match_score, haversine_km)

logger = logging.getLogger(__name__)

class MatchingPolicy:
    IDENTITY_REVIEW_THRESHOLD = 0.50
    SEARCHABLE_TYPES = (
        AnimalReportType.PERDIDO,
        AnimalReportType.ENCONTRADO,
        AnimalReportType.EN_TRANSITO,
    )

    def __init__(self, legacy_threshold=0.35):
        if not 0 < legacy_threshold <= 1:
            raise ValueError("El umbral visual anterior debe estar entre 0 (excluido) y 1.")
        self.legacy_threshold = legacy_threshold

    @staticmethod
    def unit_vector(value, size=None):
        if not isinstance(value, list):
            raise ValueError("Se esperaba una lista de componentes.")
        vector = np.asarray(value, dtype=float)
        if vector.ndim != 1 or not vector.size or (size is not None and vector.size != size):
            raise ValueError("Dimensión de vector inválida.")
        norm = np.linalg.norm(vector)
        if not np.isfinite(norm) or norm <= 0:
            raise ValueError("Vector visual inválido.")
        return vector / norm

    @staticmethod
    def context(target, candidate):
        distance = haversine_km(target.latitude, target.longitude, candidate.latitude, candidate.longitude)
        semantic = calculate_semantic_similarity(
            target.color_description, target.pet_breed, target.description,
            candidate.color_description, candidate.pet_breed, candidate.description,
        )
        return distance, semantic

    def candidate_types(self, report_type):
        # Dos personas pueden publicar al mismo animal con el mismo tipo de reporte.
        # Adopciones y alertas no participan de la búsqueda de mascotas.
        return self.SEARCHABLE_TYPES if report_type in self.SEARCHABLE_TYPES else ()

    def score(self, target, candidate, embedding):
        if incompatible_coat_colors(target.color_description, candidate.color_description):
            return None
        other = json.loads(candidate.embedding)
        if isinstance(embedding, dict):
            return self.score_identity(target, candidate, embedding, other)
        if not isinstance(embedding, list) or not isinstance(other, list):
            return None
        first = self.unit_vector(embedding)
        second = self.unit_vector(other, first.size)
        visual = calculate_cosine_similarity(first.tolist(), second.tolist())
        if visual < self.legacy_threshold:
            return None
        distance, semantic = self.context(target, candidate)
        return {"report": candidate, "visual_similarity": visual,
                "semantic_similarity": semantic, "distance_km": distance,
                "combined_score": calculate_pet_match_score(visual, distance, semantic_sim=semantic)}

    def score_identity(self, target, candidate, embedding, other):
        if not isinstance(other, dict) or embedding["version"] != other.get("version"):
            return None
        threshold = float(embedding["threshold"])
        if not np.isfinite(threshold) or not 0 <= threshold <= 1.000001:
            return None
        first = self.unit_vector(embedding["vector"])

        def vectors(report, primary):
            yield report.image_path, self.unit_vector(primary["vector"], first.size)
            for photo in report.additional_photos:
                try:
                    extra = json.loads(photo.embedding or "null")
                    if isinstance(extra, dict) and extra.get("version") == primary["version"]:
                        yield photo.image_path, self.unit_vector(extra["vector"], first.size)
                except (ValueError, TypeError, KeyError):
                    logger.warning("Embedding inválido en foto %s", photo.id)

        target_paths, target_vectors = zip(*vectors(target, embedding))
        other_paths, other_vectors = zip(*vectors(candidate, other))
        similarities = np.asarray(target_vectors) @ np.asarray(other_vectors).T
        row, column = np.unravel_index(similarities.argmax(), similarities.shape)
        visual = float(np.clip(similarities[row, column], -1.0, 1.0))
        if not np.isfinite(visual) or visual < min(threshold, self.IDENTITY_REVIEW_THRESHOLD):
            return None
        distance, semantic = self.context(target, candidate)
        return {"report": candidate, "visual_similarity": round(max(0.0, visual), 3),
                "semantic_similarity": semantic, "distance_km": distance, "combined_score": max(0.0, visual),
                "query_image_path": target_paths[row], "matched_image_path": other_paths[column],
                "review_only": visual < threshold}

class MatchingService:
    REVIEW_LIMIT = 3

    def __init__(self, reports, policy=None):
        self.reports = reports
        self.policy = policy or MatchingPolicy()

    def find(self, target, top_k=5):
        if not target.embedding:
            return [], []
        try:
            embedding = json.loads(target.embedding)
        except (ValueError, TypeError):
            return [], []
        candidates = self.reports.matching_candidates(target, self.policy.candidate_types(target.report_type))
        scored = []
        for candidate in candidates:
            try:
                score = self.policy.score(target, candidate, embedding)
            except (ValueError, TypeError, KeyError):
                logger.warning("Embedding inválido en reporte %s", candidate.id)
                continue
            if score is not None:
                scored.append(score)
        scored.sort(key=lambda item: (
            -item["visual_similarity"], -(item["semantic_similarity"] or 0.0), item["distance_km"],
        ))
        matches = [item for item in scored if not item.get("review_only")]
        review = [item for item in scored if item.get("review_only")]
        return matches[:top_k], review[:self.REVIEW_LIMIT]
