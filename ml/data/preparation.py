"""Validación y balanceo local reproducible; no descarga ni altera los originales."""
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from ml.taxonomy import LABEL_TO_IDX

class DatasetValidator:
    def validate(self, records, image_root=Path('.')):
        errors = []
        seen = {}
        for index, record in enumerate(records):
            if record.get("label") not in LABEL_TO_IDX:
                errors.append(f"Registro {index}: etiqueta desconocida")
            if record.get("split") not in ("train", "val", "test"):
                errors.append(f"Registro {index}: split inválido")
            image = record.get("image")
            if not image or not (Path(image_root) / image).is_file():
                errors.append(f"Registro {index}: imagen inexistente")
            if not isinstance(record.get("text"), str):
                errors.append(f"Registro {index}: texto inválido")
            identity = str((Path(image_root) / image).resolve()) if image else None
            if identity in seen and seen[identity] != record.get("split"):
                errors.append(f"Registro {index}: imagen compartida entre splits")
            seen[identity] = record.get("split")
        return errors

class DatasetPreparation:
    def __init__(self, seed=42):
        self.seed = seed
        self.validator = DatasetValidator()

    def balance_train(self, records, per_class):
        if per_class < 1:
            raise ValueError("per_class debe ser positivo")
        groups = defaultdict(list)
        preserved = []
        for record in records:
            if record["split"] == "train":
                groups[record["label"]].append(record)
            else:
                preserved.append(record)
        rng = random.Random(self.seed)
        # Submuestreo: nunca duplicar ejemplos entre train, val y test.
        return preserved + [record for group in groups.values()
                            for record in rng.sample(group, min(per_class, len(group)))]

    def run(self, source, output=None, per_class=None, image_root=Path('.')):
        records = json.loads(Path(source).read_text())
        errors = self.validator.validate(records, image_root)
        if errors:
            raise ValueError("\n".join(errors))
        prepared = self.balance_train(records, per_class) if per_class is not None else records
        if output:
            Path(output).write_text(json.dumps(prepared, indent=2, ensure_ascii=False))
        return {"samples": len(prepared), "classes": dict(Counter(r["label"] for r in prepared))}
