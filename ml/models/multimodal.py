import torch
import torch.nn as nn
from .vit_encoder import ViTEncoder
from .roberta_encoder import RobertaEncoder
from .cross_attention import CrossAttentionFusion

class BolivarMultimodalModel(nn.Module):
    """
    Modelo final que unifica ViT + RoBERTa + Cross-Attention + Classification Head.
    Clasifica problemáticas urbanas, animales y tránsito en N categorías.
    """
    def __init__(self, num_classes=None, embed_dim=768, freeze_encoders=True):
        super(BolivarMultimodalModel, self).__init__()
        if num_classes is None:
            from ml.taxonomy import NUM_CLASSES as _N
            num_classes = _N
        
        # 1. Encoders
        self.vit = ViTEncoder(freeze_layers=freeze_encoders)
        self.roberta = RobertaEncoder(freeze_layers=freeze_encoders)
        
        # 2. Cross-Attention Fusion
        self.fusion = CrossAttentionFusion(embed_dim=embed_dim, num_heads=8, dropout=0.1)
        
        # 3. Classification Head (MLP): 768 -> 512 -> 256 -> N clases
        self.classifier = nn.Sequential(
            nn.Linear(embed_dim, 512),
            nn.GELU(),
            nn.Dropout(0.30),
            nn.Linear(512, 256),
            nn.GELU(),
            nn.Dropout(0.20),
            nn.Linear(256, num_classes)
        )
        
    def forward(self, pixel_values, input_ids, attention_mask):
        """
        Inputs:
            pixel_values: Tensor de imágenes (B, 3, 224, 224)
            input_ids: Tokens de texto de RoBERTa (B, seq_len)
            attention_mask: Máscara de atención de texto (B, seq_len)
            
        Output:
            logits: Predicciones crudas (B, num_classes)
        """
        # A. Extraer características visuales y de texto
        # visual_tokens: (B, 197, 768)
        visual_tokens = self.vit(pixel_values)
        
        # text_tokens: (B, seq_len, 768)
        text_tokens = self.roberta(input_ids, attention_mask)
        
        # B. Fusión mediante Cross-Attention (Query=Texto, Key=Value=Imagen)
        # fused_features: (B, seq_len, 768)
        fused_features = self.fusion(text_tokens=text_tokens, visual_tokens=visual_tokens)
        
        # C. Mean Pooling: Promediamos sobre la dimensión de la secuencia de texto
        # Aplicamos la máscara de atención para no promediar los tokens de padding
        # mask shape: (B, seq_len, 1)
        mask_expanded = attention_mask.unsqueeze(-1).expand(fused_features.size()).float()
        
        # Sumamos los features multiplicados por la máscara, y dividimos por la cantidad real de tokens
        sum_features = torch.sum(fused_features * mask_expanded, dim=1)
        valid_lengths = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
        
        # mean_pooled: (B, 768)
        mean_pooled = sum_features / valid_lengths
        
        # D. Classification Head
        logits = self.classifier(mean_pooled)
        
        return logits
