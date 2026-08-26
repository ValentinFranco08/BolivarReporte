"""
train_multimodal.py — Modelo C: Multimodal (ViT + RoBERTa + Cross-Attention)
==============================================================================
Entrena el modelo multimodal completo que fusiona imagen y texto.

Arquitectura:
  ViT → Visual Tokens
  RoBERTa → Text Tokens
  Cross-Attention (Q=Texto, K=V=Imagen)
  Mean Pooling → MLP Head → 14 clases

Fases:
  Fase 1: Encoders congelados. Solo Cross-Attention + MLP Head.
  Fase 2: Descongelar últimas 2 capas de ViT.
  Fase 3: Descongelar últimas 2 capas de RoBERTa.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from transformers import RobertaTokenizer
from sklearn.metrics import f1_score, accuracy_score

from ml.datasets.multimodal_dataset import get_dataloaders, NUM_CLASSES, IDX_TO_LABEL
from ml.models.multimodal import BolivarMultimodalModel


# -----------------------------------------------------------------------
# Configuración
# -----------------------------------------------------------------------
CONFIG = {
    "dataset_path":        "ml/datasets/dataset.json",
    "checkpoint_dir":      "ml/checkpoints/multimodal",
    "tokenizer_name":      "bertin-project/bertin-roberta-base-spanish",
    "batch_size":          8,
    "max_token_length":    128,
    "num_workers":         0,
    # Fase 1: solo Fusion + Head
    "lr_head":             1e-4,
    "epochs_phase1":       10,
    # Fase 2: + últimas 2 capas ViT
    "lr_vit":              1e-5,
    "epochs_phase2":       10,
    # Fase 3: + últimas 2 capas RoBERTa
    "lr_roberta":          1e-5,
    "epochs_phase3":       10,
    "weight_decay":        0.01,
    "early_stop_patience": 5,
    "grad_clip":           1.0,
}


# -----------------------------------------------------------------------
# Utilidades
# -----------------------------------------------------------------------
def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, all_preds, all_labels = 0.0, [], []

    with torch.no_grad():
        for batch in loader:
            pixel_values   = batch["pixel_values"].to(device)
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["label"].to(device)

            logits = model(pixel_values, input_ids, attention_mask)
            loss   = criterion(logits, labels)

            total_loss += loss.item()
            all_preds.extend(logits.argmax(dim=-1).cpu().tolist())
            all_labels.extend(labels.cpu().tolist())

    avg_loss = total_loss / len(loader)
    acc      = accuracy_score(all_labels, all_preds)
    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    return avg_loss, acc, macro_f1


def train_one_epoch(model, loader, optimizer, criterion, device, grad_clip):
    model.train()
    total_loss, all_preds, all_labels = 0.0, [], []

    for batch in loader:
        pixel_values   = batch["pixel_values"].to(device)
        input_ids      = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels         = batch["label"].to(device)

        optimizer.zero_grad()
        logits = model(pixel_values, input_ids, attention_mask)
        loss   = criterion(logits, labels)
        loss.backward()

        if grad_clip > 0:
            nn.utils.clip_grad_norm_(model.parameters(), grad_clip)

        optimizer.step()

        total_loss += loss.item()
        all_preds.extend(logits.argmax(dim=-1).cpu().tolist())
        all_labels.extend(labels.cpu().tolist())

    avg_loss = total_loss / len(loader)
    acc      = accuracy_score(all_labels, all_preds)
    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    return avg_loss, acc, macro_f1


def build_optimizer(model, config, phase):
    """Construye el optimizador con diferentes LR por componente según la fase."""
    param_groups = []

    # Cross-Attention + Fusion siempre entrenables
    param_groups.append({
        "params": model.fusion.parameters(),
        "lr": config["lr_head"],
    })
    param_groups.append({
        "params": model.classifier.parameters(),
        "lr": config["lr_head"],
    })

    if phase >= 2:
        vit_trainable = [p for p in model.vit.parameters() if p.requires_grad]
        if vit_trainable:
            param_groups.append({"params": vit_trainable, "lr": config["lr_vit"]})

    if phase >= 3:
        roberta_trainable = [p for p in model.roberta.parameters() if p.requires_grad]
        if roberta_trainable:
            param_groups.append({"params": roberta_trainable, "lr": config["lr_roberta"]})

    return AdamW(param_groups, weight_decay=config["weight_decay"])


def run_phase(model, train_loader, val_loader, optimizer, scheduler, criterion,
              device, epochs, phase_name, checkpoint_dir, patience, grad_clip):
    best_val_f1 = 0.0
    no_improve  = 0
    history     = []

    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    best_path = checkpoint_dir / f"best_{phase_name}.pt"

    print(f"\n{'='*60}")
    print(f"  {phase_name.upper()} — {epochs} epochs | device: {device}")
    print(f"{'='*60}")

    for epoch in range(1, epochs + 1):
        t0 = time.time()

        train_loss, train_acc, train_f1 = train_one_epoch(
            model, train_loader, optimizer, criterion, device, grad_clip
        )
        val_loss, val_acc, val_f1 = evaluate(model, val_loader, criterion, device)

        scheduler.step()
        elapsed = time.time() - t0

        print(
            f"  Epoch {epoch:02d}/{epochs} | "
            f"train_loss={train_loss:.4f} acc={train_acc:.3f} f1={train_f1:.3f} | "
            f"val_loss={val_loss:.4f} acc={val_acc:.3f} f1={val_f1:.3f} | "
            f"{elapsed:.1f}s"
        )

        row = dict(epoch=epoch, phase=phase_name,
                   train_loss=train_loss, train_acc=train_acc, train_f1=train_f1,
                   val_loss=val_loss, val_acc=val_acc, val_f1=val_f1)
        history.append(row)

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            no_improve  = 0
            torch.save(model.state_dict(), best_path)
            print(f"  ✅ Nuevo mejor modelo guardado (val_f1={val_f1:.4f})")
        else:
            no_improve += 1
            if no_improve >= patience:
                print(f"  ⏹  Early stopping activado ({patience} epochs sin mejora).")
                break

    return history, best_val_f1, best_path


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------
def main():
    device         = get_device()
    checkpoint_dir = Path(CONFIG["checkpoint_dir"])

    print(f"\n{'='*60}")
    print(f"  BOLÍVAR RESPONDE — Modelo C: Multimodal (ViT + RoBERTa + Cross-Attention)")
    print(f"  Dispositivo: {device}")
    print(f"{'='*60}")

    tokenizer = RobertaTokenizer.from_pretrained(CONFIG["tokenizer_name"])
    train_loader, val_loader, test_loader = get_dataloaders(
        CONFIG["dataset_path"],
        tokenizer,
        batch_size=CONFIG["batch_size"],
        max_token_length=CONFIG["max_token_length"],
        num_workers=CONFIG["num_workers"],
    )

    criterion   = nn.CrossEntropyLoss()
    all_history = []

    # ─────────────────────────────────────────────────────────────────
    # FASE 1: Encoders congelados — Cross-Attention + MLP Head
    # ─────────────────────────────────────────────────────────────────
    model = BolivarMultimodalModel(num_classes=NUM_CLASSES, freeze_encoders=True).to(device)

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total     = sum(p.numel() for p in model.parameters())
    print(f"\n  Parámetros entrenables Fase 1: {trainable:,} / {total:,}")

    optimizer1 = build_optimizer(model, CONFIG, phase=1)
    scheduler1 = CosineAnnealingLR(optimizer1, T_max=CONFIG["epochs_phase1"])

    hist1, _, best_path1 = run_phase(
        model, train_loader, val_loader, optimizer1, scheduler1, criterion,
        device, CONFIG["epochs_phase1"], "fase1",
        checkpoint_dir, CONFIG["early_stop_patience"], CONFIG["grad_clip"],
    )
    all_history.extend(hist1)

    # ─────────────────────────────────────────────────────────────────
    # FASE 2: Descongelar últimas 2 capas de ViT
    # ─────────────────────────────────────────────────────────────────
    print("\n  Descongelando últimas 2 capas del ViT para Fase 2...")
    model.load_state_dict(torch.load(best_path1, map_location=device))
    model.vit.unfreeze_last_n_layers(n_layers=2)

    trainable2 = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Parámetros entrenables Fase 2: {trainable2:,} / {total:,}")

    optimizer2 = build_optimizer(model, CONFIG, phase=2)
    scheduler2 = CosineAnnealingLR(optimizer2, T_max=CONFIG["epochs_phase2"])

    hist2, _, best_path2 = run_phase(
        model, train_loader, val_loader, optimizer2, scheduler2, criterion,
        device, CONFIG["epochs_phase2"], "fase2",
        checkpoint_dir, CONFIG["early_stop_patience"], CONFIG["grad_clip"],
    )
    all_history.extend(hist2)

    # ─────────────────────────────────────────────────────────────────
    # FASE 3: Descongelar últimas 2 capas de RoBERTa
    # ─────────────────────────────────────────────────────────────────
    print("\n  Descongelando últimas 2 capas de RoBERTa para Fase 3...")
    model.load_state_dict(torch.load(best_path2, map_location=device))
    model.roberta.unfreeze_last_n_layers(n_layers=2)

    trainable3 = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Parámetros entrenables Fase 3: {trainable3:,} / {total:,}")

    optimizer3 = build_optimizer(model, CONFIG, phase=3)
    scheduler3 = CosineAnnealingLR(optimizer3, T_max=CONFIG["epochs_phase3"])

    hist3, _, best_path3 = run_phase(
        model, train_loader, val_loader, optimizer3, scheduler3, criterion,
        device, CONFIG["epochs_phase3"], "fase3",
        checkpoint_dir, CONFIG["early_stop_patience"], CONFIG["grad_clip"],
    )
    all_history.extend(hist3)

    # ─────────────────────────────────────────────────────────────────
    # Evaluación final en test
    # ─────────────────────────────────────────────────────────────────
    print("\n  Cargando mejor modelo para evaluación en TEST...")
    model.load_state_dict(torch.load(best_path3, map_location=device))
    test_loss, test_acc, test_macro_f1 = evaluate(model, test_loader, criterion, device)

    print(f"\n{'='*60}")
    print(f"  RESULTADOS FINALES — Modelo C (Multimodal)")
    print(f"  test_loss = {test_loss:.4f}")
    print(f"  test_acc  = {test_acc:.4f}  ({test_acc*100:.1f}%)")
    print(f"  macro_f1  = {test_macro_f1:.4f}")
    print(f"{'='*60}")

    results = {
        "model":           "multimodal",
        "test_loss":       test_loss,
        "test_acc":        test_acc,
        "test_macro_f1":   test_macro_f1,
        "config":          CONFIG,
        "history":         all_history,
    }
    results_path = checkpoint_dir / "results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  📄 Resultados guardados en: {results_path}")


if __name__ == "__main__":
    main()
