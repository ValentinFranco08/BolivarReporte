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


from .llm_categorizer import suggest_category

SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.70"))


class BolivarAI:
    """Servicio singleton de inferencia multimodal y búsqueda semántica."""

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

    def extract_embedding(self, image_bytes: bytes, text: str) -> Optional[list]:
        """Extrae el embedding multimodal L2-normalizado de 768 dimensiones."""
        if not self.ready:
            return None
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            pixel_values = self.transform(image).unsqueeze(0).to(self.device)

            encoding = self.tokenizer(
                text or "reporte urbano",
                padding="max_length",
                truncation=True,
                max_length=MAX_TOKEN_LENGTH,
                return_tensors="pt",
            )
            input_ids = encoding["input_ids"].to(self.device)
            attention_mask = encoding["attention_mask"].to(self.device)

            with torch.no_grad():
                _, embeddings = self.model(pixel_values, input_ids, attention_mask, return_embeddings=True)
                return embeddings[0].cpu().tolist()
        except Exception as e:
            print(f"Error extrayendo embedding: {e}")
            return None

    def predict(
        self,
        image_bytes: bytes,
        text: str,
        category_centroids: Optional[list] = None
    ) -> dict:
        """
        Realiza predicción multimodal e integra detección de categorías dinámicas
        a través de búsqueda de similitud coseno con centroides.

        category_centroids: lista opcional de dicts:
            [{"name": str, "area": str, "centroid": list[float]}, ...]
        """
        description = text.strip() if text else ""

        # Si el modelo no está cargado, operamos en modo generativo/fallback sin romper la app
        if not self.ready:
            suggested = suggest_category(description)
            mock_predictions = [{"label": suggested["name"], "score": suggested["confidence"]}]
            classification = classify_label(suggested["name"], suggested["confidence"])
            classification["category"] = suggested["area"].lower().replace(" ", "_")
            classification["label"] = suggested["name"]

            return {
                "predictions": mock_predictions,
                "classification": classification,
                "embedding": None,
                "is_novel_category": True,
                "similarity_score": 0.0,
                "suggested_category": suggested["name"],
                "suggested_label": suggested["label"],
                "suggested_area": suggested["area"],
                "suggested_description": suggested["description"],
                "model_version": "fallback-heuristico",
            }

        try:
            # 1. Procesar imagen
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            pixel_values = self.transform(image).unsqueeze(0).to(self.device)

            # 2. Tokenizar texto
            encoding = self.tokenizer(
                description or "reporte urbano",
                padding="max_length",
                truncation=True,
                max_length=MAX_TOKEN_LENGTH,
                return_tensors="pt",
            )
            input_ids = encoding["input_ids"].to(self.device)
            attention_mask = encoding["attention_mask"].to(self.device)

            # 3. Inferencia con extracción de embeddings
            with torch.no_grad():
                logits, embeddings_tensor = self.model(
                    pixel_values, input_ids, attention_mask, return_embeddings=True
                )
                probs = F.softmax(logits, dim=-1)[0]

            query_embedding = embeddings_tensor[0] # (768,) normalizado L2
            query_list = query_embedding.cpu().tolist()

            k = min(3, probs.numel())
            top_scores, top_indices = torch.topk(probs, k=k)
            predictions = []
            for score, idx in zip(top_scores, top_indices):
                idx_i = idx.item()
                label = IDX_TO_LABEL.get(idx_i, f"clase_{idx_i}")
                predictions.append({"label": label, "score": round(score.item(), 4)})

            top = predictions[0] if predictions else {"label": "desconocido", "score": 0.0}
            classification = classify_label(top["label"], top["score"])

            # 4. Búsqueda Vectorial contra Centroides Dinámicos
            best_sim = -1.0
            best_cat = None

            if category_centroids:
                for cat in category_centroids:
                    c_vec = cat.get("centroid")
                    if c_vec and len(c_vec) == len(query_list):
                        # Similitud Coseno (producto punto de vectores normalizados)
                        sim = sum(q * c for q, c in zip(query_list, c_vec))
                        if sim > best_sim:
                            best_sim = sim
                            best_cat = cat

            # Decisión de Novedad (¿Es una problemática nueva o encaja con algo conocido?)
            # Se considera nueva si:
            # - Si hay centroides y la máxima similitud es < SIMILARITY_THRESHOLD
            # - O si no hay centroides pero la confianza de la red base es baja (< 0.50)
            is_novel = False
            if category_centroids and len(category_centroids) > 0:
                is_novel = best_sim < SIMILARITY_THRESHOLD
            elif top["score"] < 0.50:
                is_novel = True

            res = {
                "predictions": predictions,
                "classification": classification,
                "embedding": query_list,
                "is_novel_category": is_novel,
                "similarity_score": round(best_sim if best_sim >= 0 else top["score"], 4),
                "model_version": self.model_version,
            }

            if is_novel:
                # Disparar propuesta de nueva categoría vía LLM / Heurística
                suggested = suggest_category(description)
                res["suggested_category"] = suggested["name"]
                res["suggested_label"] = suggested["label"]
                res["suggested_area"] = suggested["area"]
                res["suggested_description"] = suggested["description"]
                
                # Modificamos la clasificación para que refleje la sugerencia
                res["classification"]["label"] = suggested["name"]
                res["classification"]["category"] = suggested["area"].lower().replace(" ", "_")
                res["classification"]["type"] = suggested["name"]
                res["classification"]["requires_review"] = True
            elif best_cat:
                res["matched_category"] = best_cat["name"]

            return res

        except Exception as e:
            return {
                "error": str(e),
                "predictions": [],
                "model_version": self.model_version
            }


# Instancia singleton
ai_service = BolivarAI()

