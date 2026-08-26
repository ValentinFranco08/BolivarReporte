import torch
import torch.nn as nn
from transformers import RobertaModel

class RobertaEncoder(nn.Module):
    """
    Encoder    Text Encoder usando bertin-project/bertin-roberta-base-spanish (RoBERTa entrenado en español).
    Extrae los 'Text Tokens' para la arquitectura multimodal.
    """
    def __init__(self, model_name="bertin-project/bertin-roberta-base-spanish", freeze_layers=True):
        super(RobertaEncoder, self).__init__()
        self.roberta = RobertaModel.from_pretrained(model_name)
        
        # Congelar todas las capas por defecto (Fase 1)
        if freeze_layers:
            for param in self.roberta.parameters():
                param.requires_grad = False
                
    def forward(self, input_ids, attention_mask):
        """
        Input: input_ids (batch_size, seq_len), attention_mask (batch_size, seq_len)
        Output: text_tokens (batch_size, seq_len, 768)
        """
        outputs = self.roberta(input_ids=input_ids, attention_mask=attention_mask, output_hidden_states=True)
        # Retornamos la secuencia completa de tokens (last_hidden_state)
        # Shape: (batch_size, sequence_length, hidden_size) = (B, L, 768)
        return outputs.last_hidden_state

    def unfreeze_last_n_layers(self, n_layers=2):
        """Descongela las últimas N capas de RoBERTa (Para Fase 3/4)."""
        # Descongelar el pooler (si existe y se usa)
        if hasattr(self.roberta, 'pooler') and self.roberta.pooler is not None:
            for param in self.roberta.pooler.parameters():
                param.requires_grad = True
                
        # Descongelar las últimas N capas del encoder
        for layer in self.roberta.encoder.layer[-n_layers:]:
            for param in layer.parameters():
                param.requires_grad = True
