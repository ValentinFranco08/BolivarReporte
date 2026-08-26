"""
Servicio de IA Multimodal para Reporte Bolívar.
Carga BolivarMultimodalModel (ViT + RoBERTa + Cross-Attention) y
realiza inferencia a partir de imagen + texto.
"""

import os
import io
import sys
import torch
import torch.nn.functional as F
from PIL import Image
from transformers import RobertaTokenizer
from torchvision import transforms

# Asegurar que Python encuentra el módulo ml/ desde backend/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../../'))
sys.path.insert(0, PROJECT_ROOT)

from ml.models.multimodal import BolivarMultimodalModel
from ml.taxonomy import LABEL_TO_IDX, IDX_TO_LABEL, NUM_CLASSES, classify_label

# -----------------------------------------------------------------------
# Configuración
# -----------------------------------------------------------------------
TOKENIZER_NAME  = "bertin-project/bertin-roberta-base-spanish"
CHECKPOINT_PATH = os.path.join(PROJECT_ROOT, "ml/checkpoints/multimodal/best_fase3.pt")
# Fallback a fase2 o fase1 si la fase3 no existe aún
FALLBACK_PATHS = [
    os.path.join(PROJECT_ROOT, "ml/checkpoints/multimodal/best_fase2.pt"),
    os.path.join(PROJECT_ROOT, "ml/checkpoints/multimodal/best_fase1.pt"),
]
MAX_TOKEN_LENGTH = 128

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]


def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


class BolivarAI:
    """Servicio singleton de inferencia multimodal."""

    def __init__(self):
        self.device = get_device()
        self.ready = False
        self.model_version = "multimodal-v1"

        print(f"Iniciando servicio de IA Multimodal en dispositivo: {self.device}")

        # Buscar el checkpoint más avanzado disponible
        checkpoint = None
        for path in [CHECKPOINT_PATH] + FALLBACK_PATHS:
            if os.path.exists(path):
                checkpoint = path
                break

        if checkpoint is None:
            print("⚠️  No se encontró ningún checkpoint del modelo multimodal.")
            print("    Ejecutá primero: python3 ml/training/train_multimodal.py")
            return

        try:
            # Tokenizer
            self.tokenizer = RobertaTokenizer.from_pretrained(TOKENIZER_NAME)

            state = torch.load(checkpoint, map_location=self.device)
            last_w = None
            for k, v in state.items():
                if k.startswith("classifier.") and k.endswith(".weight"):
                    last_w = v
            ckpt_classes = int(last_w.shape[0]) if last_w is not None else NUM_CLASSES

            self.model = BolivarMultimodalModel(
                num_classes=ckpt_classes,
                freeze_encoders=False
            ).to(self.device)

            self.model.load_state_dict(state)
            self.num_classes = ckpt_classes
            self.model.eval()

            # Transformaciones de imagen (igual que eval)
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
            ])

            self.model_version = f"multimodal-v1 ({os.path.basename(checkpoint)})"
            self.ready = True
            print(f"✅ Modelo Multimodal cargado: {checkpoint}")

        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")

    def predict(self, image_bytes: bytes, text: str) -> dict:
        """
        Realiza predicción multimodal (imagen + texto).

        Returns:
            {
                "predictions": [{"label": str, "score": float}, ...],
                "model_version": str
            }
        """
        if not self.ready:
            return {
                "error": "El modelo de IA no está disponible. Entrenamiento pendiente.",
                "predictions": [],
                "model_version": "none"
            }

        try:
            # 1. Procesar imagen
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            pixel_values = self.transform(image).unsqueeze(0).to(self.device)  # (1, 3, 224, 224)

            # 2. Tokenizar texto
            encoding = self.tokenizer(
                text,
                padding="max_length",
                truncation=True,
                max_length=MAX_TOKEN_LENGTH,
                return_tensors="pt",
            )
            input_ids      = encoding["input_ids"].to(self.device)        # (1, L)
            attention_mask = encoding["attention_mask"].to(self.device)    # (1, L)

            # 3. Inferencia
            with torch.no_grad():
                logits = self.model(pixel_values, input_ids, attention_mask)
                probs  = F.softmax(logits, dim=-1)[0]

            k = min(3, probs.numel())
            top_scores, top_indices = torch.topk(probs, k=k)
            predictions = []
            for score, idx in zip(top_scores, top_indices):
                idx_i = idx.item()
                label = IDX_TO_LABEL.get(idx_i, f"clase_{idx_i}")
                predictions.append({"label": label, "score": round(score.item(), 4)})

            top = predictions[0] if predictions else {"label": "desconocido", "score": 0.0}
            classification = classify_label(top["label"], top["score"])

            return {
                "predictions": predictions,
                "classification": classification,
                "model_version": self.model_version,
            }

        except Exception as e:
            return {"error": str(e), "predictions": [], "model_version": self.model_version}


# Instancia singleton
ai_service = BolivarAI()
