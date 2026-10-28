"""Exportar feedback al contrato de datos de ML sin acoplar ML a SQLAlchemy."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]

def export_retraining_dataset(output_file: str):
    from app.database import SessionLocal
    from app.dependencies import get_feedback_service
    from app.core.config import settings
    with SessionLocal() as session:
        samples = get_feedback_service(session).training_samples(settings.uploads_dir)
    Path(output_file).write_text(json.dumps(samples, indent=2, ensure_ascii=False))
    print(f"Exportadas {len(samples)} correcciones a {output_file}")
    return samples

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exportar correcciones para ML (image, text, label, feedback_id)")
    parser.add_argument("--output", default="retraining_dataset.json")
    args = parser.parse_args()
    export_retraining_dataset(args.output)
