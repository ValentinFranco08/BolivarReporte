"""Entrenar en DogReID-1553 y evaluar externamente en MPDD."""
import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path

import torch
from transformers import ViTModel

from ml.device import get_device
from ml.evaluation.reid_reports import compare_photo_counts
from ml.models.pet_reid import PetReIDModel
from ml.training.reid import extract, train_projection


def dogreid_splits(images, splits):
    with splits.open(newline="") as file:
        rows = list(csv.DictReader(file, delimiter="\t"))
    training = [row for row in rows if row["SPLIT_OPEN_SET"] == "train"]
    identities = sorted({row["DOG_ID"] for row in training})
    random.Random(42).shuffle(identities)
    validation_ids = set(identities[:120])
    absent_ids = set(identities[:40])
    groups = {
        (row["DOG_ID"], row["GROUP"])
        for row in training if row["DOG_ID"] in validation_ids
    }
    query_groups = {}
    for identity, group in sorted(groups):
        query_groups.setdefault(identity, group)

    parts = {key: [] for key in ("train", "val_query", "val_gallery", "test_query", "test_gallery")}
    for row in rows:
        dog, video = row["DOG_ID"], row["VIDEO_ID"]
        split = row["SPLIT_OPEN_SET"]
        if split != "train":
            key = f"test_{split}"
        elif dog not in validation_ids:
            key = "train"
        elif dog in absent_ids or row["GROUP"] == query_groups[dog]:
            key = "val_query"
        else:
            key = "val_gallery"
        parts[key].append((images / dog / f"{dog}-{video}.jpg", dog))
    counts = Counter(label for _, label in parts["train"])
    parts["train"] = [row for row in parts["train"] if counts[row[1]] >= 2]
    return parts


def mpdd_splits(root):
    def rows(split):
        return [(path, path.name.split("_")[0]) for path in sorted((root / split).glob("*.jpg"))]

    query, gallery = rows("query"), rows("gallery")
    identities = sorted({label for _, label in gallery})
    random.Random(42).shuffle(identities)
    enrolled = set(identities[:len(identities) // 2])
    return query, [row for row in gallery if row[1] in enrolled]


@torch.no_grad()
def project_pairs(model, pairs):
    return tuple((model.project(features), labels) for features, labels in pairs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--splits", type=Path, required=True)
    parser.add_argument("--mpdd", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    torch.manual_seed(42)

    parts = dogreid_splits(args.images, args.splits)
    parts["mpdd_query"], parts["mpdd_gallery"] = mpdd_splits(args.mpdd)
    reference = torch.load(args.reference, map_location="cpu", weights_only=True)
    device = get_device()
    model = PetReIDModel(ViTModel.from_pretrained(reference["encoder"])).to(device).eval()
    features = {}
    for name, rows in parts.items():
        print(f"{name}: {len(rows)} fotos en {device}", flush=True)
        features[name] = extract(model, rows, device, batch_size=16)
    model.cpu()
    validation = features["val_query"], features["val_gallery"]
    test = features["test_query"], features["test_gallery"]
    external = features["mpdd_query"], features["mpdd_gallery"]

    baseline = compare_photo_counts(validation, test, external)
    model.projection.load_state_dict(reference["projection"])
    faces = compare_photo_counts(*(project_pairs(model, pair) for pair in (validation, test, external)))

    # Elegir época y umbral solo con las consultas de validación de DogReID.
    model.projection.reset_parameters()
    _, weights = train_projection(
        model, features["train"], validation, epochs=12, seed=42, photos_per_report=3,
    )
    model.projection.load_state_dict(weights)
    body = compare_photo_counts(*(project_pairs(model, pair) for pair in (validation, test, external)))

    result = {"vit": baseline, "dogfacenet": faces, "dogreid": body, "counts": {
        key: {"photos": len(rows), "dogs": len({label for _, label in rows})}
        for key, rows in parts.items()
    }}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "format": 1, "encoder": reference["encoder"], "projection": weights,
        "threshold": body["1"]["dogreid"]["threshold"],
    }, args.output)
    args.output.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
