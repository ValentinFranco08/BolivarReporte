import torch.nn as nn
from ml.taxonomy import NUM_CLASSES
from .vit_encoder import ViTEncoder
from .roberta_encoder import RobertaEncoder

class ViTClassifier(nn.Module):
    def __init__(self, num_classes=NUM_CLASSES, freeze=True):
        super().__init__()
        self.vit = ViTEncoder(freeze_layers=freeze)
        hidden = 768

        self.classifier = nn.Sequential(
            nn.Linear(hidden, 512),
            nn.GELU(),
            nn.Dropout(0.30),
            nn.Linear(512, 256),
            nn.GELU(),
            nn.Dropout(0.20),
            nn.Linear(256, num_classes),
        )

    def forward(self, pixel_values, **kwargs):
        # Usamos el CLS token (posición 0) como representación global
        tokens = self.vit(pixel_values)          # (B, 197, 768)
        cls_token = tokens[:, 0, :]              # (B, 768)
        return self.classifier(cls_token)

class RobertaClassifier(nn.Module):
    def __init__(self, num_classes=NUM_CLASSES, freeze=True):
        super().__init__()
        self.roberta = RobertaEncoder(freeze_layers=freeze)
        hidden = 768

        self.classifier = nn.Sequential(
            nn.Linear(hidden, 512),
            nn.GELU(),
            nn.Dropout(0.30),
            nn.Linear(512, 256),
            nn.GELU(),
            nn.Dropout(0.20),
            nn.Linear(256, num_classes),
        )

    def forward(self, input_ids, attention_mask, **kwargs):
        # Usamos el CLS token (posición 0) como representación global
        tokens    = self.roberta(input_ids, attention_mask)  # (B, seq_len, 768)
        cls_token = tokens[:, 0, :]                          # (B, 768)
        return self.classifier(cls_token)
