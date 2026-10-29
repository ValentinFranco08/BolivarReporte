"""Inferencia multimodal independiente de FastAPI y SQLAlchemy."""
import os
import io
from pathlib import Path
from typing import Optional
import torch
import torch.nn.functional as F
from PIL import Image
from transformers import RobertaTokenizer
from ml.models.multimodal import BolivarMultimodalModel
from ml.taxonomy import NUM_CLASSES, classify_label
from ml.device import get_device
from ml.preprocessing.images import ImagePreprocessor, smart_animal_crop
from ml.preprocessing.text import TextPreprocessor
from .checkpoints import CheckpointLoader
from .category_suggester import suggest_category

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOKENIZER_NAME = "bertin-project/bertin-roberta-base-spanish"
CHECKPOINT_PATH = PROJECT_ROOT / "ml/checkpoints/multimodal/best_multimodal_finetuned.pt"
FALLBACK_PATHS = [PROJECT_ROOT / f"ml/checkpoints/multimodal/best_fase{phase}.pt" for phase in (3, 2, 1)]
MAX_TOKEN_LENGTH = 128
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.70"))

class MultimodalPredictor:
    """Encapsula el modelo, preprocesamiento e inferencia multimodal."""

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
            print("    Ejecutá primero: python -m ml.cli train --model multimodal")
            return

        try:
            artifact = CheckpointLoader().load(checkpoint, self.device)
            self.tokenizer = RobertaTokenizer.from_pretrained(
                artifact.config.get("tokenizer_name", TOKENIZER_NAME)
            )
            state = artifact.state_dict
            ckpt_classes = artifact.num_classes
            self.idx_to_label = dict(enumerate(artifact.labels))

            self.model = BolivarMultimodalModel(
                num_classes=ckpt_classes,
                freeze_encoders=False
            ).to(self.device)

            self.model.load_state_dict(state)
            self.num_classes = ckpt_classes
            self.model.eval()

            # Transformaciones de imagen (igual que eval)
            self.transform = ImagePreprocessor()
            self.text_preprocessor = TextPreprocessor(
                self.tokenizer, artifact.config.get("max_token_length", MAX_TOKEN_LENGTH)
            )

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

            encoding = self.text_preprocessor(text)
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
            encoding = self.text_preprocessor(description)
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
                label = self.idx_to_label.get(idx_i, f"clase_{idx_i}")
                predictions.append({"label": label, "score": round(score.item(), 4)})

            top = predictions[0] if predictions else {"label": "desconocido", "score": 0.0}
            classification = classify_label(top["label"], top["score"])

            # 4. Búsqueda Vectorial contra Centroides Dinámicos
            best_sim = -1.0
            best_cat = None

            valid_centroids = [cat for cat in (category_centroids or [])
                               if cat.get("centroid") and len(cat["centroid"]) == len(query_list)]
            if valid_centroids:
                matrix = torch.tensor([cat["centroid"] for cat in valid_centroids], device=self.device)
                similarities = matrix @ query_embedding
                best_index = int(similarities.argmax().item())
                best_sim = float(similarities[best_index].item())
                best_cat = valid_centroids[best_index]

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

    def extract_pet_embedding(self, image_bytes: bytes) -> list:
        """
        Extrae un vector representativo L2-normalizado de 768 dimensiones para
        cotejo visual de mascotas (Pet Re-Identification).
        Implementa Auto-Crop focal + multi-escala sobre el Vision Transformer (ViT [CLS] + spatial pooling),
        aislando rasgos anatómicos del pelaje y rostro del animal sin contaminación del fondo.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            # Si el modelo multimodal está listo, usar extracción directa de alta resolución de ViT
            if self.ready:
                # 1. Vista Global
                pv_global = self.transform(image).unsqueeze(0).to(self.device)
                
                # 2. Vista Focal (Auto-Crop enfocado en el animal)
                focused_img = smart_animal_crop(image)
                pv_focal = self.transform(focused_img).unsqueeze(0).to(self.device)
                
                with torch.no_grad():
                    # Extraer tokens del Vision Transformer (B, 197, 768)
                    v_glob = self.model.vit(pv_global)
                    feat_glob = F.normalize(0.7 * v_glob[:, 0, :] + 0.3 * v_glob[:, 1:, :].mean(dim=1), p=2, dim=-1)
                    
                    v_foc = self.model.vit(pv_focal)
                    feat_foc = F.normalize(0.7 * v_foc[:, 0, :] + 0.3 * v_foc[:, 1:, :].mean(dim=1), p=2, dim=-1)
                    
                    # Fusión multi-escala: 60% detalles focales (hocico, manchas) + 40% proporciones globales
                    combined = F.normalize(0.6 * feat_foc + 0.4 * feat_glob, p=2, dim=-1)
                    return combined[0].cpu().tolist()
            
            # Fallback determinista si el modelo no estuviera en memoria
            resized = smart_animal_crop(image).resize((16, 16))
            import numpy as np
            arr = np.array(resized, dtype=np.float32) / 255.0
            flat = arr.flatten()
            norm = np.linalg.norm(flat)
            if norm > 0:
                flat = flat / norm
            return flat.tolist()
        except Exception as e:
            print(f"Error extrayendo embedding de mascota: {e}")
            return [0.0] * 768
