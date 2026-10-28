"""Orquestación de experimentos ViT, RoBERTa y multimodal mediante composición."""
import argparse
import json
from pathlib import Path
from collections import Counter
import random
import numpy as np
import torch
from torch import nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from ml.device import get_device
from ml.taxonomy import IDX_TO_LABEL, LABEL_TO_IDX, NUM_CLASSES
from ml.inference.checkpoints import CheckpointLoader
from .engine import Trainer, TrainingPhase, ADAPTERS

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def load_config(kind, path=None):
    location = Path(path) if path else PROJECT_ROOT / "ml" / "configs" / f"{kind}.json"
    return json.loads(location.read_text())

class OptimizerFactory:
    """LR por componente y sin weight decay para bias/norm."""
    def create(self, model, config):
        rates = {"vit": config.get("lr_vit", config["lr_head"]),
                 "roberta": config.get("lr_roberta", config["lr_head"])}
        groups = {}
        for name, parameter in model.named_parameters():
            if not parameter.requires_grad:
                continue
            component = name.split(".", 1)[0]
            rate = rates.get(component, config["lr_head"])
            decay = 0.0 if any(token in name.lower() for token in ("bias", "norm")) else config["weight_decay"]
            groups.setdefault((rate, decay), []).append(parameter)
        return AdamW([{"params": params, "lr": rate, "weight_decay": decay}
                      for (rate, decay), params in groups.items()])

class ExperimentRunner:
    def __init__(self, kind, config, model_factory=None, loader_factory=None):
        self.kind = kind
        self.config = dict(config)
        self.model_factory = model_factory
        self.loader_factory = loader_factory
        self.checkpoints = CheckpointLoader()

    def create_model(self):
        if self.model_factory:
            return self.model_factory()
        from ml.models.baselines import ViTClassifier, RobertaClassifier
        from ml.models.multimodal import BolivarMultimodalModel
        factories = {"vit": ViTClassifier, "roberta": RobertaClassifier,
                     "multimodal": BolivarMultimodalModel}
        return factories[self.kind]()

    def create_loaders(self):
        if self.loader_factory:
            return self.loader_factory()
        from transformers import RobertaTokenizer
        from ml.data.dataset import get_dataloaders
        config = self.config
        from ml.data.preparation import DatasetValidator
        records = json.loads(self.resolve(config["dataset_path"]).read_text())
        errors = DatasetValidator().validate(records, PROJECT_ROOT)
        if errors:
            raise ValueError("Dataset inválido: " + "; ".join(errors[:10]))
        return get_dataloaders(self.resolve(config["dataset_path"]),
            RobertaTokenizer.from_pretrained(config["tokenizer_name"]),
            batch_size=config["batch_size"], max_token_length=config["max_token_length"],
            num_workers=config["num_workers"])

    @staticmethod
    def resolve(path):
        location = Path(path)
        return location if location.is_absolute() else PROJECT_ROOT / location

    def phases(self):
        config = self.config
        second = "roberta" if self.kind == "roberta" else "vit"
        phases = [TrainingPhase("fase1", config["epochs_phase1"]),
            TrainingPhase("fase2", config["epochs_phase2"],
                ((second, config.get(f"unfreeze_{second}_layers", 2)),))]
        if self.kind == "multimodal":
            phases.append(TrainingPhase("fase3", config["epochs_phase3"],
                (("roberta", config["unfreeze_roberta_layers"]),)))
        return phases

    def criterion(self):
        if self.kind != "multimodal":
            return nn.CrossEntropyLoss()
        records = json.loads(self.resolve(self.config["dataset_path"]).read_text())
        counts = Counter(record["label"] for record in records if record["split"] == "train")
        weights = torch.tensor([sum(counts.values()) / (NUM_CLASSES * max(1, counts[label]))
                                for label in LABEL_TO_IDX], dtype=torch.float)
        return nn.CrossEntropyLoss(weight=weights / weights.mean())

    def run(self, skip_phase1=False):
        seed = self.config.get("seed", 42)
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        device = get_device()
        loaders = self.create_loaders()
        model = self.create_model().to(device)
        labels = [IDX_TO_LABEL[i] for i in sorted(IDX_TO_LABEL)]
        trainer = Trainer(model, ADAPTERS[self.kind](), self.criterion().to(device), device,
                          labels, self.config, self.checkpoints)
        directory = self.resolve(self.config["checkpoint_dir"])
        history = []
        best_path = None
        for index, phase in enumerate(self.phases()):
            path = directory / f"best_{phase.name}.pt"
            if index == 0 and skip_phase1:
                artifact = self.checkpoints.load(path, device)
                if artifact.labels != tuple(labels):
                    raise ValueError("El checkpoint utiliza otra taxonomía")
                model.load_state_dict(artifact.state_dict)
                best_path = path
                continue
            phase.prepare(model)
            optimizer = OptimizerFactory().create(model, self.config)
            scheduler = CosineAnnealingLR(optimizer, T_max=phase.epochs)
            rows, _, best_path = trainer.run_phase(loaders[0], loaders[1], optimizer, scheduler,
                phase, directory, self.config["early_stop_patience"], self.config["grad_clip"])
            history.extend(rows)
            model.load_state_dict(self.checkpoints.load(best_path, device).state_dict)
        loss, accuracy, f1, report, matrix = trainer.evaluator.evaluate(model, loaders[2], trainer.criterion, detailed=True)
        results = dict(model=self.kind, test_loss=loss, test_acc=accuracy, test_macro_f1=f1,
            classification_report=report, confusion_matrix=matrix.tolist(), config=self.config, history=history)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "results.json").write_text(json.dumps(results, indent=2))
        if self.kind == "multimodal":
            # El archivo final conserva el estado de optimizador y el de la mejor época.
            import shutil
            shutil.copy2(best_path, directory / "best_multimodal_finetuned.pt")
        return results

def training_main(kind, argv=None):
    parser = argparse.ArgumentParser(description=f"Entrenamiento {kind}")
    parser.add_argument("--config")
    for phase in (1, 2, 3):
        parser.add_argument(f"--epochs-phase{phase}", type=int)
    for component in ("head", "vit", "roberta"):
        parser.add_argument(f"--lr-{component}", type=float)
    parser.add_argument("--unfreeze-vit", type=int)
    parser.add_argument("--unfreeze-roberta", type=int)
    parser.add_argument("--skip-phase1", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar configuración sin cargar pesos")
    args = parser.parse_args(argv)
    config = load_config(kind, args.config)
    overrides = {key: value for key, value in vars(args).items()
                 if value is not None and key in config}
    config.update(overrides)
    for component in ("vit", "roberta"):
        count = getattr(args, f"unfreeze_{component}")
        if count is not None:
            config[f"unfreeze_{component}_layers"] = count
    runner = ExperimentRunner(kind, config)
    if args.dry_run:
        print(json.dumps({"model": kind, "config": config,
                          "phases": [phase.name for phase in runner.phases()]}, indent=2))
        return
    runner.run(skip_phase1=args.skip_phase1)
