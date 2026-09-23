"""
Taxonomía oficial de Reporte Bolívar, incluido el módulo Tránsito y Estacionamiento.

La IA clasifica la situación visual/textual. No determina infracción legal:
eso queda en un rule engine municipal (fuera de este módulo).
"""

from __future__ import annotations

# Leaf label → índice (6 clases). Orden estable para entrenar/inferir.
LABEL_TO_IDX = {
    "abandono": 0,
    "animal_en_riesgo": 1,
    "animal_encontrado": 2,
    "animal_perdido": 3,
    "animal_suelto": 4,
    "posible_animal_herido": 5,
}

IDX_TO_LABEL = {v: k for k, v in LABEL_TO_IDX.items()}
NUM_CLASSES = len(LABEL_TO_IDX)

CONFIDENCE_REVIEW_THRESHOLD = 0.55

# Jerarquía pedida en el módulo: category / subcategory / type
HIERARCHY = {}

AREA_BY_LABEL = {
    "animal_perdido": "Animales",
    "animal_encontrado": "Animales",
    "animal_suelto": "Animales",
    "animal_en_riesgo": "Animales",
    "posible_animal_herido": "Animales",
    "abandono": "Animales",
}

# Prioridad operativa (no calificación legal)
PRIORITY_BY_LABEL = {
    "animal_perdido": "media",
    "animal_encontrado": "media",
    "animal_suelto": "media",
    "animal_en_riesgo": "alta",
    "posible_animal_herido": "alta",
    "abandono": "alta",
}

FOLDER_TO_LABEL = {
    "animals_animal_abandonado": "abandono",
    "animals_animal_en_riesgo": "animal_en_riesgo",
    "animals_animal_encontrado": "animal_encontrado",
    "animals_animal_perdido": "animal_perdido",
    "animals_animal_suelto": "animal_suelto",
    "animals_posible_animal_herido": "posible_animal_herido",
}

TRANSIT_FOLDERS = []

SEED_CATEGORIES = [
    {"name": "animal_perdido", "area": "Animales", "description": "Mascota perdida buscando a su dueño"},
    {"name": "animal_encontrado", "area": "Animales", "description": "Mascota encontrada y retenida o avistada"},
    {"name": "animal_suelto", "area": "Animales", "description": "Perro o animal suelto en la vía pública"},
    {"name": "animal_en_riesgo", "area": "Animales", "description": "Animal en situación de peligro"},
    {"name": "posible_animal_herido", "area": "Animales", "description": "Animal con signos de lastimaduras o enfermedad"},
    {"name": "abandono", "area": "Animales", "description": "Mascota abandonada recientemente"},
]

DISCLAIMER = (
    "La IA clasifica la situación a partir de la foto y el texto. "
    "No determina una infracción legal; eso corresponde a la normativa municipal."
)


def classify_label(label: str, confidence: float) -> dict:
    hier = HIERARCHY.get(
        label,
        {
            "category": AREA_BY_LABEL.get(label, "general").lower().replace(" ", "_"),
            "subcategory": label,
            "type": label,
        },
    )
    requires_review = confidence < CONFIDENCE_REVIEW_THRESHOLD
    return {
        **hier,
        "type": hier["type"],
        "label": label,
        "confidence": round(float(confidence), 4),
        "requires_review": requires_review,
        "priority": PRIORITY_BY_LABEL.get(label, "media"),
        "legal_status": "sin_calificacion_legal",
        "disclaimer": DISCLAIMER,
    }
