"""
train_multimodal.py — Modelo C: Multimodal (ViT + RoBERTa + Cross-Attention)
==============================================================================
Entrena y realiza Fine-Tuning Progresivo sobre el modelo multimodal completo.

Fases de Fine-Tuning:
  Fase 1: Encoders congelados. Entrena Cross-Attention + Classification Head (LR=1e-4).
  Fase 2: Descongela las últimas N capas del Vision Transformer (ViT) con LR discriminativo (LR=1.5e-5).
  Fase 3: Descongela las últimas N capas de RoBERTa-BNE con LR discriminativo (LR=1.5e-5).

Mejoras avanzadas:
  - Discriminación de Learning Rate por componente y tipo de parámetro (sin decay en bias/norm).
  - Ponderación de clases automática en CrossEntropyLoss para balancear el dataset.
  - Reporte detallado de métricas por clase (Precision, Recall, F1) en test.
  - Guarda automáticamente el checkpoint 'best_multimodal_finetuned.pt'.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import argparse
import json
import time
import shutil
from pathlib import Path
from collections import Counter

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from transformers import RobertaTokenizer
from sklearn.metrics import f1_score, accuracy_score, classification_report, confusion_matrix

from ml.datasets.multimodal_dataset import get_dataloaders, NUM_CLASSES, IDX_TO_LABEL
from ml.models.multimodal import BolivarMultimodalModel


# -----------------------------------------------------------------------
# Configuración por defecto
# -----------------------------------------------------------------------
DEFAULT_CONFIG = {
    "dataset_path":            "ml/datasets/dataset.json",
    "checkpoint_dir":          "ml/checkpoints/multimodal",
    "tokenizer_name":          "bertin-project/bertin-roberta-base-spanish",
    "batch_size":              8,
    "max_token_length":        128,
    "num_workers":             0,
    # Fase 1: solo Fusion + Head
    "lr_head":                 1e-4,
    "epochs_phase1":           10,
    # Fase 2: + últimas capas ViT
    "lr_vit":                  1.5e-5,
    "unfreeze_vit_layers":     3,
    "epochs_phase2":           10,
    # Fase 3: + últimas capas RoBERTa
    "lr_roberta":              1.5e-5,
    "unfreeze_roberta_layers": 3,
    "epochs_phase3":           10,
    "weight_decay":            0.01,
    "early_stop_patience":     5,
    "grad_clip":               1.0,
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


def compute_class_weights(dataset_path, device):
    """Calcula pesos inversos de clase para mitigar desbalance en train."""
    try:
        with open(dataset_path, "r", encoding="utf-8") as f:
            records = json.load(f)
        train_labels = [r["label"] for r in records if r.get("split") == "train"]
        counts = Counter(train_labels)
        total = len(train_labels)
        from ml.taxonomy import LABEL_TO_IDX
        weights = [1.0] * NUM_CLASSES
        for lbl, idx in LABEL_TO_IDX.items():
            cnt = counts.get(lbl, 1)
            weights[idx] = total / (NUM_CLASSES * cnt)
        w_tensor = torch.tensor(weights, dtype=torch.float, device=device)
        # Normalizar para mantener escala del loss
        w_tensor = w_tensor / w_tensor.mean()
        return w_tensor
    except Exception as e:
        print(f"⚠️  No se pudieron calcular class weights ({e}), usando loss uniforme.")
        return None


def evaluate(model, loader, criterion, device, detailed: bool = False):
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

    avg_loss = total_loss / max(1, len(loader))
    acc      = accuracy_score(all_labels, all_preds)
    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    
    if detailed:
        target_names = [IDX_TO_LABEL.get(i, f"clase_{i}") for i in range(NUM_CLASSES)]
        report = classification_report(all_labels, all_preds, target_names=target_names, digits=4, zero_division=0)
        cm = confusion_matrix(all_labels, all_preds)
        return avg_loss, acc, macro_f1, report, cm
        
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

    avg_loss = total_loss / max(1, len(loader))
    acc      = accuracy_score(all_labels, all_preds)
    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    return avg_loss, acc, macro_f1


def build_optimizer(model, config, phase):
    """
    Construye el optimizador AdamW con grupos discriminativos de parámetros:
    - LR diferenciado por componente (Head vs ViT vs RoBERTa)
    - Exclusión de Weight Decay en parámetros de bias y LayerNorm (Best Practice)
    """
    param_groups = []
    weight_decay = config["weight_decay"]

    def add_component_params(named_params, lr):
        decay_params = []
        no_decay_params = []
        for name, p in named_params:
            if not p.requires_grad:
                continue
            if any(nd in name.lower() for nd in ["bias", "layernorm", "layer_norm", "norm"]):
                no_decay_params.append(p)
            else:
                decay_params.append(p)
        if decay_params:
            param_groups.append({"params": decay_params, "lr": lr, "weight_decay": weight_decay})
        if no_decay_params:
            param_groups.append({"params": no_decay_params, "lr": lr, "weight_decay": 0.0})

    # 1. Cross-Attention + Classification Head (siempre entrenables)
    add_component_params(model.fusion.named_parameters(), config["lr_head"])
    add_component_params(model.classifier.named_parameters(), config["lr_head"])

    # 2. ViT fine-tuning
    if phase >= 2:
        vit_named = list(model.vit.named_parameters())
        add_component_params(vit_named, config["lr_vit"])

    # 3. RoBERTa fine-tuning
    if phase >= 3:
        roberta_named = list(model.roberta.named_parameters())
        add_component_params(roberta_named, config["lr_roberta"])

    return AdamW(param_groups)


def run_phase(model, train_loader, val_loader, optimizer, scheduler, criterion,
              device, epochs, phase_name, checkpoint_dir, patience, grad_clip):
    best_val_f1 = 0.0
    no_improve  = 0
    history     = []

    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    best_path = checkpoint_dir / f"best_{phase_name}.pt"

    print(f"\n{'='*65}")
    print(f"  🚀 {phase_name.upper()} — {epochs} epochs | Dispositivo: {device}")
    print(f"{'='*65}")

    for epoch in range(1, epochs + 1):
        t0 = time.time()

        train_loss, train_acc, train_f1 = train_one_epoch(
            model, train_loader, optimizer, criterion, device, grad_clip
        )
        val_loss, val_acc, val_f1 = evaluate(model, val_loader, criterion, device)

        if scheduler:
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
            print(f"  ✅ Nuevo mejor modelo guardado (val_macro_f1={val_f1:.4f})")
        else:
            no_improve += 1
            if no_improve >= patience:
                print(f"  ⏹  Early stopping activado ({patience} epochs sin mejora en {phase_name}).")
                break

    return history, best_val_f1, best_path


# -----------------------------------------------------------------------
# Pipeline Principal
# -----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Fine-Tuning Progresivo Multimodal (ViT + RoBERTa)")
    parser.add_argument("--epochs-phase1", type=int, default=DEFAULT_CONFIG["epochs_phase1"], help="Epochs fase 1")
    parser.add_argument("--epochs-phase2", type=int, default=DEFAULT_CONFIG["epochs_phase2"], help="Epochs fase 2")
    parser.add_argument("--epochs-phase3", type=int, default=DEFAULT_CONFIG["epochs_phase3"], help="Epochs fase 3")
    parser.add_argument("--unfreeze-vit", type=int, default=DEFAULT_CONFIG["unfreeze_vit_layers"], help="Capas ViT a descongelar")
    parser.add_argument("--unfreeze-roberta", type=int, default=DEFAULT_CONFIG["unfreeze_roberta_layers"], help="Capas RoBERTa a descongelar")
    parser.add_argument("--lr-head", type=float, default=DEFAULT_CONFIG["lr_head"], help="LR para Classifier y Cross-Attention")
    parser.add_argument("--lr-vit", type=float, default=DEFAULT_CONFIG["lr_vit"], help="LR para capas ViT")
    parser.add_argument("--lr-roberta", type=float, default=DEFAULT_CONFIG["lr_roberta"], help="LR para capas RoBERTa")
    parser.add_argument("--skip-phase1", action="store_true", help="Saltear Fase 1 si ya existe best_fase1.pt")
    args = parser.parse_args()

    config = dict(DEFAULT_CONFIG)
    config.update({
        "epochs_phase1": args.epochs_phase1,
        "epochs_phase2": args.epochs_phase2,
        "epochs_phase3": args.epochs_phase3,
        "unfreeze_vit_layers": args.unfreeze_vit,
        "unfreeze_roberta_layers": args.unfreeze_roberta,
        "lr_head": args.lr_head,
        "lr_vit": args.lr_vit,
        "lr_roberta": args.lr_roberta,
    })

    device = get_device()
    checkpoint_dir = Path(config["checkpoint_dir"])
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"  🐾 BOLÍVAR ANIMAL — FINE-TUNING PROGRESIVO MULTIMODAL")
    print(f"  Dispositivo activo: {device}")
    print(f"  Capas descongeladas: ViT={config['unfreeze_vit_layers']} | RoBERTa={config['unfreeze_roberta_layers']}")
    print(f"  Learning rates: Head={config['lr_head']} | ViT={config['lr_vit']} | RoBERTa={config['lr_roberta']}")
    print(f"{'='*70}")

    tokenizer = RobertaTokenizer.from_pretrained(config["tokenizer_name"])
    train_loader, val_loader, test_loader = get_dataloaders(
        config["dataset_path"],
        tokenizer,
        batch_size=config["batch_size"],
        max_token_length=config["max_token_length"],
        num_workers=config["num_workers"],
    )

    class_weights = compute_class_weights(config["dataset_path"], device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    all_history = []

    best_path1 = checkpoint_dir / "best_fase1.pt"

    # ─────────────────────────────────────────────────────────────────
    # FASE 1: Encoders congelados — Cross-Attention + MLP Head
    # ─────────────────────────────────────────────────────────────────
    if args.skip_phase1 and best_path1.exists():
        print(f"\n  ⏩ Saltando Fase 1: utilizando checkpoint existente: {best_path1}")
        model = BolivarMultimodalModel(num_classes=NUM_CLASSES, freeze_encoders=True).to(device)
        model.load_state_dict(torch.load(best_path1, map_location=device))
    else:
        model = BolivarMultimodalModel(num_classes=NUM_CLASSES, freeze_encoders=True).to(device)
        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total     = sum(p.numel() for p in model.parameters())
        print(f"\n  [FASE 1] Parámetros entrenables: {trainable:,} / {total:,} ({trainable/total*100:.2f}%)")

        optimizer1 = build_optimizer(model, config, phase=1)
        scheduler1 = CosineAnnealingLR(optimizer1, T_max=config["epochs_phase1"], eta_min=1e-6)

        hist1, _, best_path1 = run_phase(
            model, train_loader, val_loader, optimizer1, scheduler1, criterion,
            device, config["epochs_phase1"], "fase1",
            checkpoint_dir, config["early_stop_patience"], config["grad_clip"],
        )
        all_history.extend(hist1)

    # ─────────────────────────────────────────────────────────────────
    # FASE 2: Descongelar últimas N capas de ViT
    # ─────────────────────────────────────────────────────────────────
    print(f"\n  Descongelando últimas {config['unfreeze_vit_layers']} capas del ViT para Fase 2...")
    model.load_state_dict(torch.load(best_path1, map_location=device))
    model.vit.unfreeze_last_n_layers(n_layers=config["unfreeze_vit_layers"])

    trainable2 = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total      = sum(p.numel() for p in model.parameters())
    print(f"  [FASE 2] Parámetros entrenables: {trainable2:,} / {total:,} ({trainable2/total*100:.2f}%)")

    optimizer2 = build_optimizer(model, config, phase=2)
    scheduler2 = CosineAnnealingLR(optimizer2, T_max=config["epochs_phase2"], eta_min=1e-6)

    hist2, _, best_path2 = run_phase(
        model, train_loader, val_loader, optimizer2, scheduler2, criterion,
        device, config["epochs_phase2"], "fase2",
        checkpoint_dir, config["early_stop_patience"], config["grad_clip"],
    )
    all_history.extend(hist2)

    # ─────────────────────────────────────────────────────────────────
    # FASE 3: Descongelar últimas N capas de RoBERTa
    # ─────────────────────────────────────────────────────────────────
    print(f"\n  Descongelando últimas {config['unfreeze_roberta_layers']} capas de RoBERTa para Fase 3...")
    model.load_state_dict(torch.load(best_path2, map_location=device))
    model.roberta.unfreeze_last_n_layers(n_layers=config["unfreeze_roberta_layers"])

    trainable3 = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  [FASE 3] Parámetros entrenables: {trainable3:,} / {total:,} ({trainable3/total*100:.2f}%)")

    optimizer3 = build_optimizer(model, config, phase=3)
    scheduler3 = CosineAnnealingLR(optimizer3, T_max=config["epochs_phase3"], eta_min=1e-6)

    hist3, _, best_path3 = run_phase(
        model, train_loader, val_loader, optimizer3, scheduler3, criterion,
        device, config["epochs_phase3"], "fase3",
        checkpoint_dir, config["early_stop_patience"], config["grad_clip"],
    )
    all_history.extend(hist3)

    # ─────────────────────────────────────────────────────────────────
    # Evaluación Final y Exportación
    # ─────────────────────────────────────────────────────────────────
    print("\n  Cargando mejor modelo final para evaluación en TEST...")
    model.load_state_dict(torch.load(best_path3, map_location=device))
    test_loss, test_acc, test_macro_f1, report, cm = evaluate(model, test_loader, criterion, device, detailed=True)

    print(f"\n{'='*70}")
    print(f"  📊 REPORTE DE EVALUACIÓN FINAL EN TEST — BOLÍVAR ANIMAL")
    print(f"  Loss: {test_loss:.4f} | Accuracy: {test_acc*100:.2f}% | Macro F1: {test_macro_f1:.4f}")
    print(f"{'='*70}")
    print(report)
    print("Matriz de confusión:")
    print(cm)
    print(f"{'='*70}")

    # Guardar checkpoint definitivo
    final_checkpoint_path = checkpoint_dir / "best_multimodal_finetuned.pt"
    shutil.copy2(best_path3, final_checkpoint_path)
    print(f"  💾 Checkpoint definitivo guardado en: {final_checkpoint_path}")

    results = {
        "model":           "multimodal_fine_tuned",
        "test_loss":       test_loss,
        "test_acc":        test_acc,
        "test_macro_f1":   test_macro_f1,
        "classification_report": report,
        "config":          config,
        "history":         all_history,
    }
    results_path = checkpoint_dir / "results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"  📄 Resultados y métricas actualizadas en: {results_path}")


if __name__ == "__main__":
    main()
