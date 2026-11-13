"""Reentrenar DINOv2 desde el manifiesto y medir precisión en pruebas reservadas."""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageOps
import torch
from transformers import AutoModel

from ml.data.reid_sampling import ScenePairSampler
from ml.device import get_device
from ml.evaluation.reid_precision import calibrate_precision, precision_metrics
from ml.evaluation.reid_reports import report_scores
from ml.models.pet_reid import PetReIDModel
from ml.preprocessing.dog_crop import DogCropper, crop_box
from ml.preprocessing.images import ImagePreprocessor
from ml.training.reid import train_projection
from ml.training.reid_compare import subgroup_results


@torch.inference_mode()
def extract_variants(model, rows, detector, device):
    variants = defaultdict(list)
    preprocess = ImagePreprocessor()
    for start in range(0, len(rows), 16):
        photos = []
        for row in rows[start:start + 16]:
            with Image.open(row["image"]) as photo:
                photos.append(ImageOps.exif_transpose(photo).convert("RGB"))
        crops = [crop_box(photo, box) if box is not None else photo
                 for photo, box in zip(photos, detector.boxes(photos))]
        for mode, images in (("full", photos), ("automatic", crops)):
            tensors = torch.stack([preprocess(image) for image in images]).to(device)
            variants[mode].append(model.features(tensors).cpu())
        if start % 400 == 0:
            print(f"{start + len(photos)}/{len(rows)} fotos", flush=True)
    return {mode: (torch.cat(features), [row["dog_id"] for row in rows])
            for mode, features in variants.items()}


def score_split(model, features, roles, count):
    query, gallery = [(model.project(features[role][0]), features[role][1]) for role in roles]
    return report_scores(query, gallery, count, top_k=6)


@torch.no_grad()
def audit(model, features, reference_threshold):
    result = {}
    for count in (1, 3, 4):
        val = score_split(model, features, ("val_query", "val_gallery"), count)
        threshold = calibrate_precision(val)
        datasets = {
            "validation": val,
            "dogreid": score_split(model, features, ("test_query", "test_gallery"), count),
            "mpdd": score_split(model, features, ("mpdd_query", "mpdd_gallery"), count),
        }
        if "local_test_query" in features or "local_test_gallery" in features:
            datasets["local"] = score_split(model, features, ("local_test_query", "local_test_gallery"), count)
        result[str(count)] = {
            "reference_threshold": {name: precision_metrics(scores, reference_threshold)
                                    for name, scores in datasets.items()},
            "calibrated": None if threshold is None else {
                name: precision_metrics(scores, threshold) for name, scores in datasets.items()
            },
        }
    return result


def precision_status(results):
    if "local" not in results["1"]["reference_threshold"]:
        return "local_test_missing"
    for scenario in results.values():
        calibrated = scenario["calibrated"]
        if calibrated is None:
            return "validation_threshold_missing"
        local = calibrated["local"]
        if local["suggestions"] < 20 or local["precision"] < 0.8:
            return "minimum_not_met"
    return "minimum_met_pending_coverage_review"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--encoder", required=True)
    parser.add_argument("--detector", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=12)
    args = parser.parse_args()
    raw = args.manifest.read_bytes()
    rows = defaultdict(list)
    for row in json.loads(raw)["photos"]:
        rows[row["role"]].append(row)
    counts = Counter(row["dog_id"] for row in rows["train"])
    rows["train"] = [row for row in rows["train"] if counts[row["dog_id"]] >= 2]
    device = get_device()
    model = PetReIDModel(AutoModel.from_pretrained(args.encoder)).to(device).eval()
    detector = DogCropper(args.detector, torch.device("cpu"))
    by_mode = defaultdict(dict)
    for role, partition in rows.items():
        print(f"Procesando {role}: {len(partition)} fotos", flush=True)
        for mode, features in extract_variants(model, partition, detector, device).items():
            by_mode[mode][role] = features
    model.cpu()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = {"manifest_sha256": hashlib.sha256(raw).hexdigest(), "seed": 42,
               "epochs": args.epochs, "minimum_precision": 0.8,
               "counts": {role: {"photos": len(items), "dogs": len({r["dog_id"] for r in items})}
                          for role, items in rows.items()},
               "local_photos": sum(r["source"] == "local" for items in rows.values() for r in items),
               "labeled_coats": len({r["dog_id"] for items in rows.values() for r in items if r.get("coat")}),
               "variants": {}}
    sampler = ScenePairSampler.from_manifest(rows["train"])
    for mode, features in by_mode.items():
        torch.manual_seed(42)
        model.projection.reset_parameters()
        validation = features["val_query"], features["val_gallery"]
        metrics, weights = train_projection(
            model, features["train"], validation, args.epochs, 42,
            photos_per_report=3, sample_batches=sampler,
        )
        model.projection.load_state_dict(weights)
        threshold = metrics["threshold"]
        with torch.no_grad():
            test = [(model.project(features[role][0]), features[role][1])
                    for role in ("test_query", "test_gallery")]
            metadata = rows["test_query"] + rows["test_gallery"]
            groups = subgroup_results(
                *test, {r["dog_id"]: r["breed"] for r in metadata if r.get("breed")},
                {r["dog_id"]: r["coat"] for r in metadata if r.get("coat")}, threshold,
            )
        precision = audit(model, features, threshold)
        results["variants"][mode] = {"precision": precision, "subgroups": groups,
                                     "local_status": precision_status(precision)}
        torch.save({
            "format": 1, "encoder": args.encoder, "projection": weights, "threshold": threshold,
            "detector": str(args.detector) if mode == "automatic" else None,
        }, args.output_dir / f"dinov2-v2-{mode}.pt")
    (args.output_dir / "dinov2-v2.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
