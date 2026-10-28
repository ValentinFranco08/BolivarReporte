"""Contrato numérico del modelo real con encoders pequeños inyectados, sin red."""
import torch
from torch import nn
from ml.models.multimodal import BolivarMultimodalModel
from ml.taxonomy import NUM_CLASSES

class TinyVision(nn.Module):
    def forward(self, pixel_values):
        return pixel_values.flatten(2).transpose(1, 2)

class TinyText(nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding = nn.Embedding(20, 8)

    def forward(self, input_ids, attention_mask):
        return self.embedding(input_ids)

def test_forward_pass():
    model = BolivarMultimodalModel(num_classes=NUM_CLASSES, embed_dim=8,
        visual_encoder=TinyVision(), text_encoder=TinyText())
    model.eval()
    with torch.no_grad():
        logits, embeddings = model(torch.randn(2, 8, 2, 2),
            torch.randint(0, 20, (2, 5)), torch.ones(2, 5), return_embeddings=True)
    assert logits.shape == (2, NUM_CLASSES)
    assert embeddings.shape == (2, 8)
    assert torch.isfinite(logits).all()
    assert torch.allclose(embeddings.norm(dim=-1), torch.ones(2), atol=1e-5)

if __name__ == "__main__":
    test_forward_pass()
