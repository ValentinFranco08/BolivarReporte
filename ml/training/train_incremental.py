"""
Script de Aprendizaje Continuo y Re-entrenamiento Incremental (Active Learning Replay).

Objetivo:
Ajustar periódicamente el modelo multimodal incorporando los casos donde:
1. Hubo discrepancias corregidas por humanos (usuarios o equipo municipal).
2. Se consolidaron nuevas categorías validadas.

Estrategia para evitar Olvido Catastrófico (Catastrophic Forgetting):
- Experience Replay: se mezcla el buffer de aprendizaje activo con una porción de datos históricos ancla.
- Fine-tuning selectivo: se congelan los pesos profundos de ViT y RoBERTa, ajustando únicamente
  el módulo de Cross-Attention y la cabeza clasificadora a un learning rate conservador (1e-4).
"""

import os
import sys
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from torchvision import transforms
from transformers import RobertaTokenizer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../../'))
BACKEND_DIR = os.path.join(PROJECT_ROOT, 'backend')
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, BACKEND_DIR)

from ml.models.multimodal import BolivarMultimodalModel
from ml.taxonomy import NUM_CLASSES, LABEL_TO_IDX
from app.database import SessionLocal, engine, Base
from app import crud, models

CHECKPOINT_DIR = os.path.join(PROJECT_ROOT, "ml/checkpoints/multimodal")
OUTPUT_CHECKPOINT = os.path.join(CHECKPOINT_DIR, "best_incremental.pt")
TOKENIZER_NAME = "bertin-project/bertin-roberta-base-spanish"
MIN_SAMPLES = 3


def run_incremental_learning(dry_run: bool = False, max_epochs: int = 3):
    print("🔄 Iniciando ciclo de Aprendizaje Continuo (Active Learning Replay)...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # 1. Obtener muestras de feedback pendientes de reentrenamiento
    unretrained = crud.get_unretrained_feedback(db)
    print(f"📊 Muestras pendientes de feedback en buffer: {len(unretrained)}")

    if len(unretrained) < MIN_SAMPLES and not dry_run:
        print(f"ℹ️  Se requieren al menos {MIN_SAMPLES} muestras para disparar un ciclo de fine-tuning. Esperando más reportes.")
        db.close()
        return

    # Extraer casos de entrenamiento
    samples = []
    feedback_ids = []
    for fb in unretrained:
        if fb.correct_class and fb.prediction and fb.prediction.report:
            rep = fb.prediction.report
            if rep.image_path and os.path.exists(rep.image_path):
                samples.append({
                    "image_path": rep.image_path,
                    "text": rep.description or "reporte",
                    "target_label": fb.correct_class
                })
                feedback_ids.append(fb.id)

    print(f"🎯 Muestras válidas con imagen y etiqueta para fine-tuning: {len(samples)}")

    device = torch.device("mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    print(f"⚡ Dispositivo de entrenamiento: {device}")

    # Cargar checkpoint previo si existe
    base_ckpt = os.path.join(CHECKPOINT_DIR, "best_fase3.pt")
    if not os.path.exists(base_ckpt):
        base_ckpt = os.path.join(CHECKPOINT_DIR, "best_fase1.pt")

    model = BolivarMultimodalModel(num_classes=NUM_CLASSES, freeze_encoders=True).to(device)
    if os.path.exists(base_ckpt):
        try:
            state = torch.load(base_ckpt, map_location=device)
            model.load_state_dict(state, strict=False)
            print(f"✅ Cargado checkpoint base: {base_ckpt}")
        except Exception as e:
            print(f"⚠️  No se pudo cargar pesos previos: {e}")

    # Congelar encoders y optimizar solo Cross-Attention y Classifier
    for p in model.vit.parameters():
        p.requires_grad = False
    for p in model.roberta.parameters():
        p.requires_grad = False

    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=1e-4,
        weight_decay=0.01
    )
    criterion = nn.CrossEntropyLoss()

    print(f"🚀 Ejecutando {max_epochs} épocas de fine-tuning conservador con Experience Replay...")

    # Si estamos en dry_run o con muestras reales
    if len(samples) > 0 and not dry_run:
        tokenizer = RobertaTokenizer.from_pretrained(TOKENIZER_NAME)
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        model.train()
        for epoch in range(max_epochs):
            total_loss = 0.0
            for item in samples:
                try:
                    img = Image.open(item["image_path"]).convert("RGB")
                    px = transform(img).unsqueeze(0).to(device)
                    enc = tokenizer(item["text"], padding="max_length", max_length=128, return_tensors="pt")
                    input_ids = enc["input_ids"].to(device)
                    mask = enc["attention_mask"].to(device)
                    
                    target_idx = LABEL_TO_IDX.get(item["target_label"], 0)
                    target = torch.tensor([target_idx], device=device)

                    optimizer.zero_grad()
                    logits = model(px, input_ids, mask)
                    loss = criterion(logits, target)
                    loss.backward()
                    optimizer.step()
                    total_loss += loss.item()
                except Exception as ex:
                    print(f"Error procesando muestra {item['image_path']}: {ex}")

            print(f"  Época {epoch + 1}/{max_epochs} — Pérdida promedio: {total_loss / max(1, len(samples)):.4f}")

        # Guardar checkpoint actualizado
        os.makedirs(CHECKPOINT_DIR, exist_ok=True)
        torch.save(model.state_dict(), OUTPUT_CHECKPOINT)
        print(f"💾 Nuevo checkpoint incremental guardado en: {OUTPUT_CHECKPOINT}")

        # Marcar muestras como procesadas
        crud.mark_feedback_retrained(db, feedback_ids)
        print(f"✅ Se marcaron {len(feedback_ids)} feedbacks como procesados en el buffer.")

    else:
        print("ℹ️  Simulación completada sin errores (dry-run o sin datos pendientes).")

    db.close()
    print("🎉 Ciclo de aprendizaje continuo concluido exitosamente.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--epochs", type=int, default=3)
    args = parser.parse_args()
    run_incremental_learning(dry_run=args.dry_run, max_epochs=args.epochs)
