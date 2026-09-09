"""
Script para inicializar los centroides vectoriales de las categorías base en Reporte Bolívar.
Permite arrancar el sistema con centroides cálidos para búsqueda semántica inmediata.

Uso:
    python3 backend/scripts/seed_centroids.py
"""

import os
import sys
import json
import math
import hashlib

# Asegurar path para importar app y ml
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, '..'))
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, PROJECT_ROOT)

from app.database import SessionLocal, engine, Base
from app import models
from ml.taxonomy import SEED_CATEGORIES


def generate_pseudo_embedding(text: str, dim: int = 768) -> list:
    """
    Genera un vector normalizado determinista a partir del texto cuando no hay GPU/pesos cargados.
    Permite probar la matemática vectorial y la búsqueda coseno sin depender de un archivo .pt pesado.
    """
    values = []
    for i in range(dim):
        h = hashlib.sha256(f"{text}_{i}".encode('utf-8')).hexdigest()
        val = (int(h[:8], 16) / 0xffffffff) * 2.0 - 1.0
        values.append(val)
    
    # L2 normalize
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


def seed_categories_and_centroids():
    # Asegurar que las tablas existan
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print(f"🌱 Sembrando categorías y centroides iniciales ({len(SEED_CATEGORIES)} categorías base)...")

    try:
        from app.ai_service import ai_service
        use_real_model = ai_service.ready
    except Exception:
        use_real_model = False

    if use_real_model:
        print("🧠 Utilizando BolivarMultimodalModel para generar embeddings visuales+textuales reales.")
    else:
        print("ℹ️  Modelo multimodal no disponible en este entorno; generando embeddings semánticos deterministas.")

    seeded = 0
    updated = 0

    for cat_data in SEED_CATEGORIES:
        name = cat_data["name"]
        area = cat_data["area"]
        desc = cat_data.get("description", "")

        cat = db.query(models.Category).filter(models.Category.name == name).first()
        if not cat:
            cat = models.Category(
                name=name,
                area=area,
                description=desc,
                active=True,
                is_verified=True,
                sample_count=1
            )
            db.add(cat)
            db.commit()
            db.refresh(cat)
            seeded += 1

        # Si no tiene centroide, lo calculamos
        if not cat.embedding_centroid:
            if use_real_model:
                # Generar imagen sintética neutra de 224x224
                from PIL import Image
                import io
                img = Image.new('RGB', (224, 224), color=(128, 128, 128))
                buf = io.BytesIO()
                img.save(buf, format='JPEG')
                vec = ai_service.extract_embedding(buf.getvalue(), f"{name}. {desc}")
            else:
                vec = generate_pseudo_embedding(f"{area} {name} {desc}")

            if vec:
                cat.embedding_centroid = json.dumps(vec)
                cat.sample_count = 1
                cat.is_verified = True
                updated += 1

    db.commit()
    print(f"✅ Proceso finalizado. Categorías nuevas creadas: {seeded}. Centroides calculados/actualizados: {updated}.")
    db.close()


if __name__ == "__main__":
    seed_categories_and_centroids()
