import torch.nn.functional as F
from torch import nn


class PetReIDModel(nn.Module):
    """ViT congelado y una proyección entrenada con identidades."""
    def __init__(self, encoder, dimensions=128):
        super().__init__()
        self.encoder = encoder.requires_grad_(False).eval()
        self.projection = nn.Linear(encoder.config.hidden_size, dimensions, bias=False)

    def features(self, images):
        tokens = self.encoder(pixel_values=images).last_hidden_state
        return F.normalize(0.7 * tokens[:, 0] + 0.3 * tokens[:, 1:].mean(dim=1), dim=1)

    def project(self, features):
        return F.normalize(self.projection(features), dim=1)

    def forward(self, images):
        return self.project(self.features(images))
