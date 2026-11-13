"""Compara DINOv2 y el cotejo anterior con la misma prueba abierta."""
import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModel

from ml.data.reid_sampling import ScenePairSampler, read_traits
from ml.device import get_device
from ml.evaluation.reid_reports import compare_photo_counts
from ml.models.pet_reid import PetReIDModel
from ml.training.reid import extract, train_projection
from ml.training.reid_body import dogreid_splits, mpdd_splits, project_pairs


def subgroup_results(query, gallery, breeds, coats, threshold):
    q, q_labels = query
    g, g_labels = gallery
    scores = (q @ g.T).clamp(-1, 1)
    def codes(traits, labels):
        mapping = {name: index for index, name in enumerate(sorted(set(traits.values())))}
        return torch.tensor([mapping.get(traits.get(dog), -1) for dog in labels])

    dogs = {dog: dog for dog in set(q_labels + g_labels)}
    same_dog = codes(dogs, q_labels)[:, None] == codes(dogs, g_labels)[None, :]
    qb, gb = codes(breeds, q_labels)[:, None], codes(breeds, g_labels)[None, :]
    labeled = (qb >= 0) & (gb >= 0)
    groups = {
        "same_dog": same_dog,
        "same_breed_different_dog": ~same_dog & labeled & (qb == gb),
        "different_breed": ~same_dog & labeled & (qb != gb),
    }
    if coats:
        qc, gc = codes(coats, q_labels)[:, None], codes(coats, g_labels)[None, :]
        groups["different_breed_same_coat"] = groups["different_breed"] & (qc >= 0) & (qc == gc)
    return {name: {"pairs": int(mask.sum()), "above_threshold": int((mask & (scores >= threshold)).sum())}
            for name, mask in groups.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--encoder", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--coats", type=Path, help="TSV con DOG_ID y COAT verificado")
    parser.add_argument("--epochs", type=int, default=12)
    args = parser.parse_args()
    torch.manual_seed(42)
    root = args.source
    splits = root / "splits.tab"
    parts = dogreid_splits(root / "Images", splits)
    parts["mpdd_query"], parts["mpdd_gallery"] = mpdd_splits(root / "MPDD/pytorch")
    breeds = read_traits(root / "breeds.tab", "BREED")
    coats = read_traits(args.coats, "COAT")
    device = get_device()
    model = PetReIDModel(AutoModel.from_pretrained(args.encoder)).to(device).eval()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    features = {}
    for name, rows in parts.items():
        print(f"{name}: {len(rows)} fotos en {device}", flush=True)
        features[name] = extract(model, rows, device, 16)
    model.cpu()
    validation = features["val_query"], features["val_gallery"]
    test = features["test_query"], features["test_gallery"]
    external = features["mpdd_query"], features["mpdd_gallery"]
    sampler = ScenePairSampler(parts["train"], splits, breeds, coats)
    result = {"frozen": compare_photo_counts(validation, test, external)}
    _, weights = train_projection(
        model, features["train"], validation, args.epochs, 42, photos_per_report=3, sample_batches=sampler,
    )
    model.projection.load_state_dict(weights)
    val, test, external = (project_pairs(model, pair) for pair in (validation, test, external))
    result["trained"] = compare_photo_counts(val, test, external)
    threshold = result["trained"]["1"]["dogreid"]["threshold"]
    result["subgroups"] = subgroup_results(*test, breeds, coats, threshold)
    result["training"] = {"photos": len(parts["train"]), "dogs": len(set(features["train"][1])),
                          "coat_labels": len(coats)}
    torch.save({"format": 1, "encoder": args.encoder, "projection": weights, "threshold": threshold}, args.output)
    args.output.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
