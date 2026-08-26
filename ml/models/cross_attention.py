import torch
import torch.nn as nn

class CrossAttentionFusion(nn.Module):
    """
    Módulo de Fusión Multimodal usando Cross-Attention.
    El Texto actúa como Query (Q), y la Imagen como Key (K) y Value (V).
    """
    def __init__(self, embed_dim=768, num_heads=8, dropout=0.1):
        super(CrossAttentionFusion, self).__init__()
        
        self.embed_dim = embed_dim
        
        # MultiHead Attention
        # batch_first=True indica que los tensores tienen forma (batch, seq, feature)
        self.multihead_attn = nn.MultiheadAttention(embed_dim=embed_dim, num_heads=num_heads, dropout=dropout, batch_first=True)
        
        # Capas de normalización
        self.layer_norm1 = nn.LayerNorm(embed_dim)
        self.layer_norm2 = nn.LayerNorm(embed_dim)
        
        # Feed Forward Network (FFN) estándar
        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim * 4, embed_dim),
            nn.Dropout(dropout)
        )
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, text_tokens, visual_tokens, text_attention_mask=None):
        """
        Q = Text Tokens (batch_size, text_seq_len, 768)
        K = Visual Tokens (batch_size, img_seq_len, 768)
        V = Visual Tokens (batch_size, img_seq_len, 768)
        
        text_attention_mask: (batch_size, text_seq_len). Se necesita invertir porque
        nn.MultiheadAttention en PyTorch usa mask donde True = ignorar.
        """
        
        # Opcional: key_padding_mask para ignorar el padding de K (pero visual_tokens no tiene padding)
        # text_attention_mask se usa normalmente si estuviéramos haciendo self-attention en texto.
        # Aquí, como el query es texto y K,V son imágenes, no necesitamos mask para la imagen,
        # PERO si queremos ignorar queries padding, PyTorch no permite un `query_padding_mask` directo.
        # De todos modos, pasamos K y V enteros.
        
        # 1. Cross Attention
        # attn_output shape: (batch_size, text_seq_len, 768)
        attn_output, _ = self.multihead_attn(query=text_tokens, key=visual_tokens, value=visual_tokens)
        
        # 2. Residual connection + LayerNorm
        x = self.layer_norm1(text_tokens + self.dropout(attn_output))
        
        # 3. FFN
        ffn_output = self.ffn(x)
        
        # 4. Residual connection + LayerNorm
        output = self.layer_norm2(x + ffn_output)
        
        return output
