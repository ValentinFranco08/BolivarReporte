"""Mide precisión de las sugerencias y calibra en perros de validación."""
import argparse
import json
from pathlib import Path

import torch

from ml.evaluation.reid import evaluate
from ml.evaluation.reid_reports import report_scores
from ml.inference.pet_predictor import PetPredictor
from ml.training.reid import extract
from ml.training.reid_body import dogreid_splits, mpdd_splits, project_pairs


def precision_metrics(scores, threshold):
    _, ranked, correct, present = scores
    suggested = ranked >= threshold
    count = int(suggested.sum())
    true = int((suggested & correct).sum())
    return {
        **evaluate((scores[0], ranked[:, :5], correct[:, :5], present), threshold),
        "precision": true / count if count else None,
        "suggestions": count,
        "correct_suggestions": true,
        "query_coverage": float(suggested.any(dim=1).float().mean()),
        "queries_with_match": int(present.sum()),
    }


def calibrate_precision(scores, minimum=0.8, min_suggestions=20):
    """Selecciona el mayor número de aciertos entre umbrales elegibles."""
    _, ranked, correct, _ = scores
    ordered, order = ranked.flatten().sort(descending=True)
    true_counts = correct.flatten()[order].cumsum(0)
    counts = torch.arange(1, len(ordered) + 1, device=ordered.device)
    # Un umbral incluye todos los puntajes empatados.
    ends = torch.cat((ordered[:-1] != ordered[1:], ordered.new_ones(1, dtype=torch.bool)))
    eligible = ends & (counts >= min_suggestions) & (true_counts >= minimum * counts)
    if not eligible.any():
        return None
    candidates = torch.where(eligible)[0]
    best = candidates[true_counts[candidates].argmax()]
    return float(ordered[best])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minimum", type=float, default=0.8)
    parser.add_argument("--min-suggestions", type=int, default=20)
    args = parser.parse_args()
    if not 0 < args.minimum <= 1 or args.min_suggestions < 1:
        parser.error("Usá una precisión entre 0 y 1 y un mínimo positivo de sugerencias.")

    root = args.source
    parts = dogreid_splits(root / "Images", root / "splits.tab")
    parts.pop("train")
    parts["mpdd_query"], parts["mpdd_gallery"] = mpdd_splits(root / "MPDD/pytorch")
    predictor = PetPredictor(args.checkpoint)
    features = {}
    for name, rows in parts.items():
        print(f"{name}: {len(rows)} fotos", flush=True)
        features[name] = extract(predictor.model, rows, predictor.device, 16, transform=predictor.preprocess)
    predictor.model.cpu()
    datasets = {
        name: project_pairs(predictor.model, (features[f"{split}_query"], features[f"{split}_gallery"]))
        for name, split in (("validation", "val"), ("dogreid", "test"), ("mpdd", "mpdd"))
    }
    result = {"checkpoint": predictor.version, "minimum_precision": args.minimum,
              "min_suggestions": args.min_suggestions, "top_k": 6, "photo_counts": {}}
    for count in (1, 3, 4):
        scores = {name: report_scores(*pair, count, top_k=6) for name, pair in datasets.items()}
        threshold = calibrate_precision(scores["validation"], args.minimum, args.min_suggestions)
        current = {name: precision_metrics(value, predictor.threshold) for name, value in scores.items()}
        calibrated = None if threshold is None else {
            name: precision_metrics(value, threshold) for name, value in scores.items()
        }
        passes = calibrated is not None and all(
            calibrated[name]["suggestions"] >= args.min_suggestions
            and calibrated[name]["precision"] >= args.minimum
            for name in ("dogreid", "mpdd")
        )
        result["photo_counts"][str(count)] = {
            "checkpoint_threshold": current, "calibrated": calibrated, "passes": passes,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
