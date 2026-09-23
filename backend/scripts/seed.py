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

        print("Poblando usuarios demo...")
        from app import auth, models
        if not db.query(models.User).filter_by(email="admin@bolivar.gob.ar").first():
            db.add(models.User(
                name="Administrador Municipal",
                email="admin@bolivar.gob.ar",
                password_hash=auth.get_password_hash("admin123"),
                role=models.UserRole.ADMIN,
            ))
        if not db.query(models.User).filter_by(email="vecino@bolivar.gob.ar").first():
            db.add(models.User(
                name="Vecino Bolívar",
                email="vecino@bolivar.gob.ar",
                password_hash=auth.get_password_hash("vecino123"),
                role=models.UserRole.CITIZEN,
            ))

        db.commit()

        print("Poblando reportes iniciales de animales y alertas...")
        import json
        admin_user = db.query(models.User).filter_by(email="admin@bolivar.gob.ar").first()
        vecino_user = db.query(models.User).filter_by(email="vecino@bolivar.gob.ar").first()
        uid = vecino_user.id if vecino_user else (admin_user.id if admin_user else None)

        if db.query(models.Report).count() == 0:
            uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
            os.makedirs(uploads_dir, exist_ok=True)
            from app.ai_service import ai_service
            import urllib.request

            demo_sources = {
                "demo_milo.jpg": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=800&auto=format&fit=crop",
                "demo_parque.jpg": "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=800&auto=format&fit=crop",
                "demo_cebo.jpg": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=800&auto=format&fit=crop",
                "demo_luna.jpg": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=800&auto=format&fit=crop",
            }
            demo_embeddings = {}
            for name, url in demo_sources.items():
                fpath = os.path.join(uploads_dir, name)
                if not os.path.exists(fpath):
                    try:
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=10) as resp, open(fpath, 'wb') as out:
                            out.write(resp.read())
                    except Exception as e:
                        print(f"No se pudo descargar {name}: {e}")
                if os.path.exists(fpath):
                    try:
                        with open(fpath, 'rb') as f:
                            demo_embeddings[name] = json.dumps(ai_service.extract_pet_embedding(f.read()))
                    except Exception as e:
                        print(f"Error extrayendo embedding para {name}: {e}")

            dummy_emb = json.dumps([0.05] * 768)

            reports_seed = [
                models.Report(
                    description="Se perdió Milo, mi labrador dorado de 3 años con collar rojo. Es muy dócil pero está asustado.",
                    latitude=-36.2335,
                    longitude=-61.1165,
                    address="Av. San Martín y Lavalle, Bolívar",
                    image_path="/uploads/demo_milo.jpg",
                    user_id=uid,
                    report_type=models.AnimalReportType.PERDIDO,
                    pet_type=models.PetType.PERRO,
                    pet_name="Milo",
                    pet_breed="Labrador Retriever",
                    color_description="Dorado / Beige",
                    health_status=models.PetHealthStatus.SANO,
                    contact_name="María López",
                    contact_phone="+5492314554433",
                    is_resolved=False,
                    embedding=demo_embeddings.get("demo_milo.jpg") or dummy_emb,
                    status=models.ReportStatus.REPORTADO,
                    priority=models.ReportPriority.HIGH
                ),
                models.Report(
                    description="Encontré perro mestizo mediano en el parque. Está esperando a su familia, le di agua y comida.",
                    latitude=-36.2255,
                    longitude=-61.1245,
                    address="Parque Las Acollaradas",
                    image_path="/uploads/demo_parque.jpg",
                    user_id=uid,
                    report_type=models.AnimalReportType.ENCONTRADO,
                    pet_type=models.PetType.PERRO,
                    pet_name="Sin nombre",
                    pet_breed="Mestizo / Barbincho",
                    color_description="Marrón claro y blanco",
                    health_status=models.PetHealthStatus.SANO,
                    contact_name="Carlos Veterinario",
                    contact_phone="+5492314889900",
                    is_resolved=False,
                    embedding=demo_embeddings.get("demo_parque.jpg") or dummy_emb,
                    status=models.ReportStatus.REPORTADO,
                    priority=models.ReportPriority.MEDIUM
                ),
                models.Report(
                    description="⚠️ URGENTE: Cebo sospechoso encontrado. Trozo de carne con polvo azul en la vereda. No transitar con mascotas.",
                    latitude=-36.2345,
                    longitude=-61.1180,
                    address="Plaza Alsina (frente al Colegio)",
                    image_path="/uploads/demo_cebo.jpg",
                    user_id=uid,
                    report_type=models.AnimalReportType.ALERTA_CEBO,
                    pet_type=models.PetType.OTRO,
                    pet_name="Alerta Cebo",
                    color_description="Carne picada con químicos",
                    health_status=models.PetHealthStatus.SINTOMAS_ENVENENAMIENTO,
                    contact_name="Guardia SAPAAB / Vecino",
                    contact_phone="+5492314112233",
                    is_resolved=False,
                    status=models.ReportStatus.REPORTADO,
                    priority=models.ReportPriority.CRITICAL
                ),
                models.Report(
                    description="Luna busca hogar definitivo. Gata de 8 meses, castrada, súper mimosa y acostumbrada a departamento.",
                    latitude=-36.2300,
                    longitude=-61.1120,
                    address="Barrio Pompeya, Bolívar",
                    image_path="/uploads/demo_luna.jpg",
                    user_id=uid,
                    report_type=models.AnimalReportType.ADOPCION,
                    pet_type=models.PetType.GATO,
                    pet_name="Luna",
                    pet_breed="Común Europeo",
                    color_description="Tricolor / Carey",
                    health_status=models.PetHealthStatus.SANO,
                    contact_name="Refugio SAPAAB",
                    contact_phone="+5492314776655",
                    is_resolved=False,
                    embedding=demo_embeddings.get("demo_luna.jpg") or dummy_emb,
                    status=models.ReportStatus.REPORTADO,
                    priority=models.ReportPriority.LOW
                )
            ]
            for rep in reports_seed:
                db.add(rep)
            db.commit()
            print("✅ 4 reportes demo sembrados (Perdido, Encontrado, Alerta Cebo, Adopción).")

        print("Seed completado exitosamente.")
    except Exception as e:
        print(f"Error durante el seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
