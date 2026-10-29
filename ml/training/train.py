"""Preparar y ejecutar un entrenamiento. Leer run_training() de arriba hacia abajo."""
import argparse
import json
import random
import shutil
from collections import Counter
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from ml.device import get_device
from ml.taxonomy import IDX_TO_LABEL, LABEL_TO_IDX, NUM_CLASSES
from .trainer import Trainer

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_path(path):
    location = Path(path)
    return location if location.is_absolute() else PROJECT_ROOT / location


def load_config(kind, path=None):
    location = Path(path) if path else PROJECT_ROOT / "ml/configs" / f"{kind}.json"
    return json.loads(location.read_text())


def create_model(kind):
    from ml.models.baselines import ViTClassifier, RobertaClassifier
    from ml.models.multimodal import BolivarMultimodalModel
    models = {"vit": ViTClassifier, "roberta": RobertaClassifier,
              "multimodal": BolivarMultimodalModel}
    return models[kind]()


def create_loaders(config):
    from transformers import RobertaTokenizer
    from ml.data.dataset import get_dataloaders
    from ml.data.preparation import DatasetValidator
    records = json.loads(resolve_path(config["dataset_path"]).read_text())
    errors = DatasetValidator().validate(records, PROJECT_ROOT)
    if errors:
        raise ValueError("Dataset inválido: " + "; ".join(errors[:10]))
    return get_dataloaders(resolve_path(config["dataset_path"]),
        RobertaTokenizer.from_pretrained(config["tokenizer_name"]),
        batch_size=config["batch_size"], max_token_length=config["max_token_length"],
        num_workers=config["num_workers"])


def create_loss(kind, config):
    if kind != "multimodal":
        return nn.CrossEntropyLoss()
    records = json.loads(resolve_path(config["dataset_path"]).read_text())
    counts = Counter(record["label"] for record in records if record["split"] == "train")
    weights = torch.tensor([sum(counts.values()) / (NUM_CLASSES * max(1, counts[label]))
                            for label in LABEL_TO_IDX], dtype=torch.float)
    return nn.CrossEntropyLoss(weight=weights / weights.mean())


def create_optimizer(model, config):
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


def training_phases(kind, config):
    phases = [("fase1", config["epochs_phase1"]), ("fase2", config["epochs_phase2"])]
    if kind == "multimodal":
        phases.append(("fase3", config["epochs_phase3"]))
    return phases


def unfreeze_layers(model, kind, phase_name, config):
    # Las capas ya habilitadas continúan entrenándose en la siguiente fase.
    if phase_name == "fase2":
        component = "roberta" if kind == "roberta" else "vit"
        count = config.get(f"unfreeze_{component}_layers", 2)
        if count > 0:
            getattr(model, component).unfreeze_last_n_layers(count)
    if phase_name == "fase3":
        count = config["unfreeze_roberta_layers"]
        if count > 0:
            model.roberta.unfreeze_last_n_layers(count)


def run_training(kind, config, skip_phase1=False):
    """1. Preparar datos/modelo. 2. Entrenar fases. 3. Evaluar y guardar resultados."""
    seed = config.get("seed", 42)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    # 1. Preparar los datos y el objeto encargado de entrenar.
    device = get_device()
    train_loader, val_loader, test_loader = create_loaders(config)
    model = create_model(kind).to(device)
    labels = tuple(IDX_TO_LABEL[i] for i in sorted(IDX_TO_LABEL))
    trainer = Trainer(model, create_loss(kind, config).to(device), device, labels, config)
    checkpoints = trainer.checkpoints
    directory = resolve_path(config["checkpoint_dir"])
    history = []

    # 2. Entrenar cada fase y recuperar sus mejores pesos antes de continuar.
    for phase_name, epochs in training_phases(kind, config):
        path = directory / f"best_{phase_name}.pt"
        if phase_name == "fase1" and skip_phase1:
            artifact = checkpoints.load(path, device)
            if artifact.labels != labels:
                raise ValueError("El checkpoint utiliza otra taxonomía")
            model.load_state_dict(artifact.state_dict)
            continue
        unfreeze_layers(model, kind, phase_name, config)
        optimizer = create_optimizer(model, config)
        scheduler = CosineAnnealingLR(optimizer, T_max=epochs)
        rows, _, path = trainer.fit(train_loader, val_loader, optimizer, scheduler,
            epochs=epochs, checkpoint_dir=directory, phase_name=phase_name,
            patience=config["early_stop_patience"], grad_clip=config["grad_clip"])
        history.extend(rows)
        model.load_state_dict(checkpoints.load(path, device).state_dict)

    # 3. Medir sobre test, que no participa de la selección de pesos.
    loss, accuracy, f1, report, matrix = trainer.evaluator.evaluate(
        model, test_loader, trainer.criterion, detailed=True)
    results = dict(model=kind, test_loss=loss, test_acc=accuracy, test_macro_f1=f1,
        classification_report=report, confusion_matrix=matrix.tolist(), config=config, history=history)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "results.json").write_text(json.dumps(results, indent=2))
    if kind == "multimodal":
        shutil.copy2(path, directory / "best_multimodal_finetuned.pt")
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
    if args.dry_run:
        print(json.dumps({"model": kind, "config": config,
                          "phases": [name for name, _ in training_phases(kind, config)]}, indent=2))
        return
    run_training(kind, config, skip_phase1=args.skip_phase1)
