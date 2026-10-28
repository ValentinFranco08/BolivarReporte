"""Aprendizaje incremental a partir de datos exportados; sin acceso al backend."""
import json
import random
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from ml.taxonomy import LABEL_TO_IDX, IDX_TO_LABEL, NUM_CLASSES
from ml.preprocessing.images import ImagePreprocessor
from ml.preprocessing.text import TextPreprocessor
from ml.inference.checkpoints import CheckpointLoader
from ml.device import get_device
from .engine import Trainer, MultimodalBatchAdapter

class FeedbackDataset(Dataset):
    def __init__(self, samples, tokenizer):
        self.samples = samples
        self.images = ImagePreprocessor()
        self.text = TextPreprocessor(tokenizer)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        item = self.samples[index]
        with Image.open(item["image"]) as image:
            pixels = self.images(image.convert("RGB"))
        encoded = self.text(item["text"])
        return {"pixel_values": pixels,
                "input_ids": encoded["input_ids"].squeeze(0),
                "attention_mask": encoded["attention_mask"].squeeze(0),
                "label": torch.tensor(LABEL_TO_IDX[item["label"]], dtype=torch.long)}

class IncrementalTrainer:
    def __init__(self, model_factory=None):
        self.model_factory = model_factory
        self.checkpoints = CheckpointLoader()

    def prepare(self, samples, historical, replay_size=32, seed=42):
        valid = [item for item in samples if item.get("label") in LABEL_TO_IDX
                 and Path(item.get("image", "")).is_file()]
        anchors = [item for item in historical if item.get("split") == "train"
                   and item.get("label") in LABEL_TO_IDX and Path(item.get("image", "")).is_file()]
        if not valid:
            raise ValueError("No hay correcciones válidas para entrenar")
        if not anchors:
            raise ValueError("Se requieren muestras históricas de train para Experience Replay")
        replay = random.Random(seed).sample(anchors, min(replay_size, len(anchors)))
        return valid, valid + replay

    def run(self, samples, historical, checkpoint, output, epochs=3, dry_run=False):
        valid, mixed = self.prepare(samples, historical)
        summary = {"feedback_ids": [item["feedback_id"] for item in valid if "feedback_id" in item],
                   "corrections": len(valid), "replay": len(mixed) - len(valid), "saved": False}
        if dry_run:
            return summary
        if epochs < 1:
            raise ValueError("epochs debe ser positivo")
        device = get_device()
        from transformers import RobertaTokenizer
        from ml.models.multimodal import BolivarMultimodalModel
        artifact = self.checkpoints.load(checkpoint, device)
        labels = tuple(IDX_TO_LABEL[i] for i in sorted(IDX_TO_LABEL))
        if artifact.labels != labels:
            raise ValueError("El checkpoint base requiere una migración explícita de taxonomía")
        model = (self.model_factory or BolivarMultimodalModel)().to(device)
        model.load_state_dict(artifact.state_dict)
        model.vit.requires_grad_(False)
        model.roberta.requires_grad_(False)
        tokenizer = RobertaTokenizer.from_pretrained("bertin-project/bertin-roberta-base-spanish")
        loader = DataLoader(FeedbackDataset(mixed, tokenizer), batch_size=8, shuffle=True)
        optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-4)
        trainer = Trainer(model, MultimodalBatchAdapter(), torch.nn.CrossEntropyLoss(), device, labels)
        for _ in range(epochs):
            trainer.train_epoch(loader, optimizer)
        self.checkpoints.save(output, model, labels=labels, optimizer=optimizer, epoch=epochs,
                              config={"training": "incremental-replay", "replay_samples": summary["replay"]})
        summary["saved"] = True
        return summary
