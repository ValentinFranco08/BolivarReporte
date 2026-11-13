"""Versionar las fotos y sus etiquetas, separadas por identidad y escena."""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from ml.data.reid_sampling import read_traits
from ml.training.reid_body import dogreid_splits, mpdd_splits

ROLES = {"train", "val_query", "val_gallery", "test_query", "test_gallery"}


def build_manifest(root, local=None, coats=None):
    splits = root / "splits.tab"
    with splits.open(newline="") as file:
        scenes = {f'{r["DOG_ID"]}-{r["VIDEO_ID"]}': r["GROUP"]
                  for r in csv.DictReader(file, delimiter="\t")}
    breeds = read_traits(root / "breeds.tab", "BREED")
    colors = read_traits(coats, "COAT")
    rows = [
        {"image": str(path), "dog_id": dog, "scene_id": scenes[path.stem], "role": role,
         "source": "dogreid", "breed": breeds.get(dog), "coat": colors.get(dog)}
        for role, photos in dogreid_splits(root / "Images", splits).items() for path, dog in photos
    ]
    for role, photos in zip(("mpdd_query", "mpdd_gallery"), mpdd_splits(root / "MPDD/pytorch")):
        rows.extend({"image": str(path), "dog_id": f"mpdd:{dog}", "scene_id": None,
                     "role": role, "source": "mpdd"} for path, dog in photos)
    if local:
        for row in json.loads(local.read_text()):
            if row.get("identity_verified") is not True or row.get("authorized") is not True:
                raise ValueError("Las fotos locales requieren identidad confirmada y autorización.")
            if row["role"] not in ROLES or not row["dog_id"].strip() or not row["scene_id"].strip():
                raise ValueError("Cada foto local necesita identidad, escena y partición válida.")
            role = row["role"]
            if role.startswith("test_"):
                role = "local_" + role
            rows.append({**row, "image": str(local.parent / row["image"]),
                         "dog_id": f'local:{row["dog_id"]}', "role": role, "source": "local"})

    partitions, scenes_by_role, seen = defaultdict(set), defaultdict(set), {}
    unique = []
    for row in rows:
        role, dog = row["role"], row["dog_id"]
        group = role.removeprefix("local_").split("_")[0]
        partitions[dog].add(group)
        if row["scene_id"] is not None:
            scenes_by_role[dog, row["scene_id"]].add(role)
        digest = hashlib.sha256(Path(row["image"]).read_bytes()).hexdigest()
        if digest in seen:
            if seen[digest] != (dog, role):
                raise ValueError(f'Foto duplicada entre identidades o particiones: {row["image"]}')
            continue
        seen[digest] = dog, role
        unique.append({**row, "sha256": digest})
    if any(len(parts) > 1 for parts in partitions.values()):
        raise ValueError("Un perro aparece en más de una partición.")
    if any(len(roles) > 1 for roles in scenes_by_role.values()):
        raise ValueError("Una escena aparece tanto en consulta como en galería.")
    return unique


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--local", type=Path, help="JSON de fotos locales verificadas")
    parser.add_argument("--coats", type=Path, help="TSV de pelaje verificado")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = build_manifest(args.source, args.local, args.coats)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"version": 1, "photos": rows}, indent=2) + "\n")
    print(dict(Counter(row["role"] for row in rows)))


if __name__ == "__main__":
    main()
