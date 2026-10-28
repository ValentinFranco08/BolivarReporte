"""Entrada CLI de aprendizaje incremental sobre archivos exportados."""
import sys
from pathlib import Path
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.training.incremental import IncrementalTrainer

def main(argv=None):
    import argparse
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument("--feedback", required=True, help="JSON con image, text, label y feedback_id opcional")
    parser.add_argument("--historical", default="ml/datasets/dataset.json")
    parser.add_argument("--checkpoint", default="ml/checkpoints/multimodal/best_multimodal_finetuned.pt")
    parser.add_argument("--output", default="ml/checkpoints/multimodal/best_incremental.pt")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--epochs", type=int, default=3)
    args = parser.parse_args(argv)
    result = IncrementalTrainer().run(json.loads(Path(args.feedback).read_text()),
        json.loads(Path(args.historical).read_text()), args.checkpoint, args.output, args.epochs, args.dry_run)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
