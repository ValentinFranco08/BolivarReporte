"""
Taxonomía oficial de Reporte Bolívar, incluido el módulo Tránsito y Estacionamiento.

La IA clasifica la situación visual/textual. No determina infracción legal:
eso queda en un rule engine municipal (fuera de este módulo).
"""

from __future__ import annotations

# Leaf label → índice (23 clases). Orden estable para entrenar/inferir.
LABEL_TO_IDX = {
    "abandono": 0,
    "animal_en_riesgo": 1,
    "animal_encontrado": 2,
    "animal_perdido": 3,
    "animal_suelto": 4,
    "arbol_caido": 5,
    "bache": 6,
    "basura": 7,
    "calle_deteriorada": 8,
    "luminaria_danada": 9,
    "microbasural": 10,
    "perdida_agua": 11,
    "posible_animal_herido": 12,
    "senalizacion_danada": 13,
    # Módulo Tránsito y Estacionamiento
    "cordon_amarillo": 14,
    "en_medio_de_calle": 15,
    "obstruccion_de_entrada": 16,
    "sobre_vereda": 17,
    "lugar_reservado": 18,
    "lugar_prohibido": 19,
    "vehiculo_abandonado": 20,
    "obstruccion_de_circulacion": 21,
    "semaforo_danado": 22,
}

IDX_TO_LABEL = {v: k for k, v in LABEL_TO_IDX.items()}
NUM_CLASSES = len(LABEL_TO_IDX)

CONFIDENCE_REVIEW_THRESHOLD = 0.55

# Jerarquía pedida en el módulo: category / subcategory / type
HIERARCHY = {
    "cordon_amarillo": {
        "category": "transito_y_estacionamiento",
        "subcategory": "estacionamiento_indebido",
        "type": "cordon_amarillo",
    },
    "en_medio_de_calle": {
        "category": "transito_y_estacionamiento",
        "subcategory": "estacionamiento_indebido",
        "type": "en_medio_de_calle",
    },
    "obstruccion_de_entrada": {
        "category": "transito_y_estacionamiento",
        "subcategory": "estacionamiento_indebido",
        "type": "obstruccion_de_entrada",
    },
    "sobre_vereda": {
        "category": "transito_y_estacionamiento",
        "subcategory": "estacionamiento_indebido",
        "type": "sobre_vereda",
    },
    "lugar_reservado": {
        "category": "transito_y_estacionamiento",
        "subcategory": "estacionamiento_indebido",
        "type": "lugar_reservado",
    },
    "lugar_prohibido": {
        "category": "transito_y_estacionamiento",
        "subcategory": "estacionamiento_indebido",
        "type": "lugar_prohibido",
    },
    "vehiculo_abandonado": {
        "category": "transito_y_estacionamiento",
        "subcategory": "vehiculo_abandonado",
        "type": "vehiculo_abandonado",
    },
    "obstruccion_de_circulacion": {
        "category": "transito_y_estacionamiento",
        "subcategory": "obstruccion_de_circulacion",
        "type": "obstruccion_de_circulacion",
    },
    "semaforo_danado": {
        "category": "transito_y_estacionamiento",
        "subcategory": "semaforo",
        "type": "semaforo_danado",
    },
    "senalizacion_danada": {
        "category": "transito_y_estacionamiento",
        "subcategory": "senalizacion_de_transito",
        "type": "senalizacion_danada",
    },
}

AREA_BY_LABEL = {
    "bache": "Infraestructura",
    "calle_deteriorada": "Infraestructura",
    "luminaria_danada": "Infraestructura",
    "arbol_caido": "Infraestructura",
    "perdida_agua": "Infraestructura",
    "senalizacion_danada": "Tránsito y Estacionamiento",
    "basura": "Higiene Urbana",
    "microbasural": "Higiene Urbana",
    "animal_perdido": "Animales",
    "animal_encontrado": "Animales",
    "animal_suelto": "Animales",
    "animal_en_riesgo": "Animales",
    "posible_animal_herido": "Animales",
    "abandono": "Animales",
    "cordon_amarillo": "Tránsito y Estacionamiento",
    "en_medio_de_calle": "Tránsito y Estacionamiento",
    "obstruccion_de_entrada": "Tránsito y Estacionamiento",
    "sobre_vereda": "Tránsito y Estacionamiento",
    "lugar_reservado": "Tránsito y Estacionamiento",
    "lugar_prohibido": "Tránsito y Estacionamiento",
    "vehiculo_abandonado": "Tránsito y Estacionamiento",
    "obstruccion_de_circulacion": "Tránsito y Estacionamiento",
    "semaforo_danado": "Tránsito y Estacionamiento",
}

# Prioridad operativa (no calificación legal)
PRIORITY_BY_LABEL = {
    "cordon_amarillo": "media",
    "en_medio_de_calle": "alta",
    "obstruccion_de_entrada": "alta",
    "sobre_vereda": "media",
    "lugar_reservado": "alta",
    "lugar_prohibido": "media",
    "vehiculo_abandonado": "media",
    "obstruccion_de_circulacion": "alta",
    "semaforo_danado": "alta",
    "senalizacion_danada": "media",
    "bache": "alta",
    "calle_deteriorada": "media",
    "luminaria_danada": "alta",
    "arbol_caido": "alta",
    "perdida_agua": "alta",
    "basura": "baja",
    "microbasural": "media",
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
    "urban_arbol_caido": "arbol_caido",
    "urban_bache": "bache",
    "urban_basura": "basura",
    "urban_calle_deteriorada": "calle_deteriorada",
    "urban_luminaria_danada": "luminaria_danada",
    "urban_microbasural": "microbasural",
    "urban_perdida_agua": "perdida_agua",
    "urban_senalizacion_danada": "senalizacion_danada",
    "transit_cordon_amarillo": "cordon_amarillo",
    "transit_en_medio_de_calle": "en_medio_de_calle",
    "transit_obstruccion_de_entrada": "obstruccion_de_entrada",
    "transit_sobre_vereda": "sobre_vereda",
    "transit_lugar_reservado": "lugar_reservado",
    "transit_lugar_prohibido": "lugar_prohibido",
    "transit_vehiculo_abandonado": "vehiculo_abandonado",
    "transit_obstruccion_de_circulacion": "obstruccion_de_circulacion",
    "transit_semaforo_danado": "semaforo_danado",
}

TRANSIT_FOLDERS = [k for k in FOLDER_TO_LABEL if k.startswith("transit_")]

SEED_CATEGORIES = [
    {"name": "bache", "area": "Infraestructura", "description": "Bache en la vía pública"},
    {"name": "calle_deteriorada", "area": "Infraestructura", "description": "Calle de tierra o pavimento muy deteriorado"},
    {"name": "luminaria_danada", "area": "Infraestructura", "description": "Foco de luz apagado o roto"},
    {"name": "arbol_caido", "area": "Infraestructura", "description": "Rama o árbol caído en la vía pública"},
    {"name": "perdida_agua", "area": "Infraestructura", "description": "Caño roto o pérdida de agua en la calle"},
    {"name": "senalizacion_danada", "area": "Tránsito y Estacionamiento", "description": "Señal de tránsito dañada, caída o ilegible"},
    {"name": "basura", "area": "Higiene Urbana", "description": "Basura suelta en la vía pública"},
    {"name": "microbasural", "area": "Higiene Urbana", "description": "Acumulación grande de basura en terrenos baldíos o esquinas"},
    {"name": "animal_perdido", "area": "Animales", "description": "Mascota perdida buscando a su dueño"},
    {"name": "animal_encontrado", "area": "Animales", "description": "Mascota encontrada y retenida o avistada"},
    {"name": "animal_suelto", "area": "Animales", "description": "Perro o animal suelto en la vía pública"},
    {"name": "animal_en_riesgo", "area": "Animales", "description": "Animal en situación de peligro"},
    {"name": "posible_animal_herido", "area": "Animales", "description": "Animal con signos de lastimaduras o enfermedad"},
    {"name": "abandono", "area": "Animales", "description": "Mascota abandonada recientemente"},
    {"name": "cordon_amarillo", "area": "Tránsito y Estacionamiento", "description": "Vehículo sobre cordón amarillo"},
    {"name": "en_medio_de_calle", "area": "Tránsito y Estacionamiento", "description": "Vehículo detenido o estacionado en medio de la calzada"},
    {"name": "obstruccion_de_entrada", "area": "Tránsito y Estacionamiento", "description": "Vehículo que obstruye una entrada o garaje"},
    {"name": "sobre_vereda", "area": "Tránsito y Estacionamiento", "description": "Vehículo estacionado sobre la vereda"},
    {"name": "lugar_reservado", "area": "Tránsito y Estacionamiento", "description": "Vehículo en lugar reservado (discapacidad, carga, etc.)"},
    {"name": "lugar_prohibido", "area": "Tránsito y Estacionamiento", "description": "Vehículo en zona de estacionamiento prohibido"},
    {"name": "vehiculo_abandonado", "area": "Tránsito y Estacionamiento", "description": "Vehículo aparentemente abandonado en la vía pública"},
    {"name": "obstruccion_de_circulacion", "area": "Tránsito y Estacionamiento", "description": "Objeto o vehículo que bloquea la circulación"},
    {"name": "semaforo_danado", "area": "Tránsito y Estacionamiento", "description": "Semáforo apagado, caído o fuera de servicio"},
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
