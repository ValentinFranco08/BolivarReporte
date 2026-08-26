import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models import Category, ModelVersion

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.taxonomy import SEED_CATEGORIES

categories_data = SEED_CATEGORIES

def seed():
    db = SessionLocal()
    try:
        print("Poblando categorías...")
        for cat_data in categories_data:
            existing = db.query(Category).filter_by(name=cat_data["name"]).first()
            if not existing:
                cat = Category(**cat_data)
                db.add(cat)
        
        print("Agregando versión del modelo Multimodal...")
        existing_model = db.query(ModelVersion).filter_by(name="multimodal-v1").first()
        if not existing_model:
            model_v1 = ModelVersion(
                name="multimodal-v1",
                version="1.0",
                architecture="ViT + RoBERTa + Cross-Attention",
                dataset_version="573_synthetic",
                macro_f1=0.6684
            )
            db.add(model_v1)

        db.commit()
        print("Seed completado exitosamente.")
    except Exception as e:
        print(f"Error durante el seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
