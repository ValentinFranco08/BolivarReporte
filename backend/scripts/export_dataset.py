import os
import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.crud import get_all_feedback

def export_retraining_dataset(output_file: str):
    db = SessionLocal()
    try:
        feedbacks = get_all_feedback(db)
        dataset = []
        
        for fb in feedbacks:
            # Solo exportamos correcciones (IA falló) para reentrenar
            if not fb.correct and fb.correct_class and fb.prediction and fb.prediction.report:
                report = fb.prediction.report
                
                dataset.append({
                    "id": report.id,
                    "image_file": os.path.basename(report.image_path),
                    "text_description": report.description or "",
                    "predicted_label": fb.prediction.predicted_class,
                    "ground_truth_label": fb.correct_class,
                    "confidence_at_prediction": fb.prediction.confidence,
                    "reviewed_by_user_id": fb.reviewed_by
                })
        
        if not dataset:
            print("No hay datos de feedback negativo para exportar.")
            return

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Dataset exportado exitosamente a: {output_file}")
        print(f"📊 Total de muestras etiquetadas para reentrenamiento: {len(dataset)}")

    except Exception as e:
        print(f"Error al exportar dataset: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exportar feedback del dashboard como dataset para reentrenamiento.")
    parser.add_argument("--output", type=str, default="retraining_dataset.json", help="Ruta del archivo JSON de salida.")
    args = parser.parse_args()
    
    export_retraining_dataset(args.output)
