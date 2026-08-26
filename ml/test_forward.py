import torch
import sys
import os

# Asegurar que Python encuentra el paquete ml
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.models.multimodal import BolivarMultimodalModel
from transformers import RobertaTokenizer

def test_forward_pass():
    print("Iniciando prueba de Forward Pass de la Arquitectura Multimodal...")
    
    # 1. Inicializar modelo
    print("Cargando modelo (esto puede tardar unos segundos si descarga los pesos)...")
    try:
        model = BolivarMultimodalModel(num_classes=14, embed_dim=768, freeze_encoders=True)
    except Exception as e:
        print(f"Error cargando modelo: {e}")
        return
        
    print("Modelo cargado exitosamente.")
    
    # 2. Preparar tensores falsos
    batch_size = 2
    
    # Imagen de prueba (B, C, H, W)
    pixel_values = torch.randn(batch_size, 3, 224, 224)
    print(f"Tensor de imagen: {pixel_values.shape}")
    
    # Texto de prueba
    tokenizer = RobertaTokenizer.from_pretrained("bertin-project/bertin-roberta-base-spanish")
    texts = ["Encontré un bache gigante en la calle San Martín.", "Hay un perro abandonado en la plaza."]
    
    inputs = tokenizer(texts, padding=True, truncation=True, max_length=128, return_tensors="pt")
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]
    print(f"Tensor de texto (input_ids): {input_ids.shape}")
    
    # 3. Forward pass
    print("Ejecutando Forward Pass...")
    model.eval() # Modo evaluación
    with torch.no_grad():
        logits = model(pixel_values, input_ids, attention_mask)
        
    print(f"Salida (logits): {logits.shape}")
    
    # Verificar dimensiones
    assert logits.shape == (batch_size, 14), f"Dimensiones incorrectas. Se esperaba {(batch_size, 14)}, se obtuvo {logits.shape}"
    
    print("\n✅ ¡Prueba de Forward Pass superada exitosamente!")
    print("La red neuronal multimodal (ViT + RoBERTa + Cross-Attention) está lista para entrenarse.")

if __name__ == "__main__":
    test()
