"""Cotejo visual con una proyección entrenada por identidad."""
import hashlib
import io
from pathlib import Path

import torch
from PIL import Image, ImageOps
from transformers import AutoModel

from ml.device import get_device
from ml.models.pet_reid import PetReIDModel
from ml.preprocessing.images import ImagePreprocessor


class PetPredictor:
    def __init__(self, checkpoint):
        raw = Path(checkpoint).read_bytes()
        artifact = torch.load(io.BytesIO(raw), map_location='cpu', weights_only=True)
        if artifact['format'] != 1:
            raise ValueError('Formato de checkpoint de cotejo desconocido.')
        self.version = 'pet-reid-' + hashlib.sha256(raw).hexdigest()[:16]
        self.threshold = float(artifact['threshold'])
        self.device = get_device()
        weights = artifact['projection']
        encoder_source = artifact['encoder']
        local_encoder = Path(__file__).resolve().parents[2] / encoder_source
        encoder = AutoModel.from_pretrained(local_encoder if local_encoder.is_dir() else encoder_source)
        self.model = PetReIDModel(encoder, weights['weight'].shape[0])
        self.model.projection.load_state_dict(weights)
        self.model.to(self.device).eval()
        self.transform = ImagePreprocessor()
        self.detector = None
        if artifact.get("detector"):
            from ml.preprocessing.dog_crop import DogCropper
            detector = Path(__file__).resolve().parents[2] / artifact["detector"]
            self.detector = DogCropper(detector, torch.device("cpu"))

    def preprocess(self, image):
        if self.detector is not None:
            from ml.preprocessing.dog_crop import crop_box
            box = next(self.detector.boxes([image]))
            if box is not None:
                image = crop_box(image, box)
        return self.transform(image)

    @torch.inference_mode()
    def embed(self, image_bytes):
        with Image.open(io.BytesIO(image_bytes)) as photo:
            image = self.preprocess(ImageOps.exif_transpose(photo).convert('RGB'))
        vector = self.model(image.unsqueeze(0).to(self.device))[0].cpu().tolist()
        return {'version': self.version, 'threshold': self.threshold, 'vector': vector}
