import torch
import torch.nn as nn
from transformers import ViTModel

class ViTEncoder(nn.Module):
    """
    Encoder Visual usando google/vit-base-patch16-224.
    Extrae los 'Visual Tokens' para su uso en la arquitectura multimodal.
    """
    def __init__(self, model_name="google/vit-base-patch16-224", freeze_layers=True):
        super(ViTEncoder, self).__init__()
        self.vit = ViTModel.from_pretrained(model_name)
        
        # Congelar todas las capas por defecto (Fase 1)
        if freeze_layers:
            for param in self.vit.parameters():
                param.requires_grad = False
                
    def forward(self, pixel_values):
        """
        Input: pixel_values (batch_size, 3, 224, 224)
        Output: visual_tokens (batch_size, 197, 768)
        """
        outputs = self.vit(pixel_values=pixel_values, output_hidden_states=True)
        # Retornamos la secuencia completa de tokens (last_hidden_state), no solo el pooler output.
        # Shape: (batch_size, sequence_length, hidden_size) = (B, 197, 768)
        return outputs.last_hidden_state

    def unfreeze_last_n_layers(self, n_layers=2):
        """Descongela las últimas N capas del ViT (Para Fase 2/4)."""
        # Descongelar el layer normalization final
        for param in self.vit.layernorm.parameters():
            param.requires_grad = True

        # Las capas del ViT están en self.vit.layers (no encoder.layer)
        for layer in self.vit.layers[-n_layers:]:
            for param in layer.parameters():
                param.requires_grad = True
