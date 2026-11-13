"""Comparar foto completa, recorte anotado y recorte automático sobre los mismos reportes."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from PIL import Image, ImageOps
import torch

from ml.evaluation.reid import calibrate, evaluate
from ml.evaluation.reid_reports import report_scores
from ml.inference.pet_predictor import PetPredictor
from ml.preprocessing.dog_crop import DogCropper, crop_box
from ml.training.reid_body import dogreid_splits


def annotations(path):
    with path.open(newline="") as file:
        boxes = {}
        for row in csv.DictReader(file, delimiter="\t"):
            x, y, width, height = (int(row[key]) for key in ("x_top_left", "y_top_left", "width", "height"))
            boxes[f'{row["DOG_ID"]}-{row["VIDEO_ID"]}'] = (x, y, x + width, y + height)
    return boxes


@torch.inference_mode()
def cropped_features(predictor, detector, annotated, rows):
    features = {mode: [] for mode in ("full", "annotated", "automatic")}
    detected = 0
    for offset in range(0, len(rows), 16):
        batch = rows[offset:offset + 16]
        images = []
        for path, _ in batch:
            with Image.open(path) as photo:
                images.append(ImageOps.exif_transpose(photo).convert("RGB"))
        auto = list(detector.boxes(images))
        detected += sum(box is not None for box in auto)
        variants = {
            "full": images,
            "annotated": [crop_box(image, annotated[path.stem]) for (path, _), image in zip(batch, images)],
            "automatic": [crop_box(image, box) if box is not None else image for image, box in zip(images, auto)],
        }
        for mode, photos in variants.items():
            tensors = torch.stack([predictor.transform(photo) for photo in photos]).to(predictor.device)
            features[mode].append(predictor.model(tensors).cpu())
        if offset % 160 == 0:
            print(f"Recortes evaluados: {min(offset + 16, len(rows))}/{len(rows)}", flush=True)
    labels = [label for _, label in rows]
    return {mode: (torch.cat(values), labels) for mode, values in features.items()}, detected


def sample(rows, labels, count):
    counts = Counter()
    selected = []
    for path, dog in rows:
        if dog in labels and counts[dog] < count:
            selected.append((path, dog))
            counts[dog] += 1
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--detector", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.source
    parts = dogreid_splits(root / "Images", root / "splits.tab")
    predictor = PetPredictor(args.checkpoint)
    detector = DogCropper(args.detector, predictor.device)
    boxes = annotations(root / "bounding_boxes.tab")
    collected, coverage = {}, {}
    for split in ("val", "test"):
        q, g = parts[f"{split}_query"], parts[f"{split}_gallery"]
        enrolled = set(sorted({dog for _, dog in g})[:64])
        absent = set(sorted({dog for _, dog in q} - {dog for _, dog in g})[:48])
        for role, rows in (("query", sample(q, enrolled | absent, 1)), ("gallery", sample(g, enrolled, 3))):
            key = f"{split}_{role}"
            collected[key], detected = cropped_features(predictor, detector, boxes, rows)
            coverage[key] = {"detected": detected, "photos": len(rows)}
    result = {"coverage": coverage, "metrics": {}}
    for mode in ("full", "annotated", "automatic"):
        result["metrics"][mode] = {}
        for count in (1, 3):
            validation = report_scores(collected["val_query"][mode], collected["val_gallery"][mode], count)
            test = report_scores(collected["test_query"][mode], collected["test_gallery"][mode], count)
            threshold = calibrate(validation)["threshold"]
            result["metrics"][mode][str(count)] = evaluate(test, threshold)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
