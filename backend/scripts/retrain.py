"""Puente explícito entre feedback persistido y el pipeline independiente de ML."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--historical", default=str(ROOT / "ml/datasets/dataset.json"))
    parser.add_argument("--checkpoint", default=str(ROOT / "ml/checkpoints/multimodal/best_multimodal_finetuned.pt"))
    parser.add_argument("--output", default=str(ROOT / "ml/checkpoints/multimodal/best_incremental.pt"))
    args = parser.parse_args()
    from app.database import SessionLocal
    from app.dependencies import get_feedback_service
    from app.core.config import settings
    from app.infrastructure.unit_of_work import UnitOfWork
    from app.repositories.feedback import FeedbackRepository
    from ml.training.incremental import IncrementalTrainer
    with SessionLocal() as session:
        samples = get_feedback_service(session).training_samples(settings.uploads_dir, pending_only=True)
        if not samples:
            print("No hay correcciones pendientes")
            return
        historical = json.loads(Path(args.historical).read_text())
        for record in historical:
            image = Path(record["image"])
            record["image"] = str(image if image.is_absolute() else ROOT / image)
        result = IncrementalTrainer().run(samples, historical, args.checkpoint, args.output,
                                          epochs=args.epochs, dry_run=args.dry_run)
        if result["saved"]:
            with UnitOfWork(session):
                FeedbackRepository(session).mark_retrained(result["feedback_ids"])
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
