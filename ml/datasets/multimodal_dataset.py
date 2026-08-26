"""
MultimodalDataset: Dataset de PyTorch que carga imagen + texto + label
desde ml/datasets/dataset.json y prepara los tensores para el modelo.

Preprocessing:
  - Imagen: Resize 224x224 + Normalization (ViT ImageNet stats) + Augmentation en train
  - Texto: Tokenización con bertin-roberta-base-spanish, max_length=128
"""

import json
import random
from pathlib import Path
from PIL import Image

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from transformers import RobertaTokenizer


from ml.taxonomy import LABEL_TO_IDX, IDX_TO_LABEL, NUM_CLASSES

# -----------------------------------------------------------------------
# Transformaciones de imagen
# -----------------------------------------------------------------------
# Estadísticas de normalización de ImageNet (ViT fue pre-entrenado con ellas)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

def get_train_transforms():
    """Augmentations para el split de entrenamiento."""
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
        transforms.RandomRotation(degrees=10),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

def get_eval_transforms():
    """Transformaciones para val y test (sin augmentación)."""
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


# -----------------------------------------------------------------------
# Dataset principal
# -----------------------------------------------------------------------
class MultimodalDataset(Dataset):
    """
    Dataset de PyTorch que carga imagen + texto + label.
    
    Args:
        json_path: Ruta al dataset.json.
        split: 'train', 'val' o 'test'.
        tokenizer: Instancia del RobertaTokenizer (ya inicializado).
        max_token_length: Longitud máxima de secuencia de texto.
        transform: Transformaciones de imagen a aplicar.
    """
    
    def __init__(
        self,
        json_path: str | Path,
        split: str,
        tokenizer: RobertaTokenizer,
        max_token_length: int = 128,
        transform=None,
    ):
        self.split = split
        self.tokenizer = tokenizer
        self.max_token_length = max_token_length
        
        # Cargar todos los registros del split solicitado
        with open(json_path, "r", encoding="utf-8") as f:
            all_records = json.load(f)
        
        self.records = [r for r in all_records if r["split"] == split]
        
        if not self.records:
            raise ValueError(f"No se encontraron registros para el split '{split}' en {json_path}")
        
        # Si no se pasan transformaciones explícitas, elegir por split
        if transform is not None:
            self.transform = transform
        elif split == "train":
            self.transform = get_train_transforms()
        else:
            self.transform = get_eval_transforms()
            
    def __len__(self) -> int:
        return len(self.records)
    
    def __getitem__(self, idx: int) -> dict:
        record = self.records[idx]
        
        # 1. Cargar y procesar imagen
        img_path = Path(record["image"])
        image = Image.open(img_path).convert("RGB")
        pixel_values = self.transform(image)
        
        # 2. Tokenizar texto
        encoding = self.tokenizer(
            record["text"],
            padding="max_length",
            truncation=True,
            max_length=self.max_token_length,
            return_tensors="pt",
        )
        
        # 3. Label numérico
        label = LABEL_TO_IDX[record["label"]]
        
        return {
            "pixel_values": pixel_values,                         # (3, 224, 224)
            "input_ids": encoding["input_ids"].squeeze(0),       # (max_token_length,)
            "attention_mask": encoding["attention_mask"].squeeze(0),  # (max_token_length,)
            "label": torch.tensor(label, dtype=torch.long),
        }


# -----------------------------------------------------------------------
# Factory de DataLoaders (conveniente para los scripts de entrenamiento)
# -----------------------------------------------------------------------
def get_dataloaders(
    json_path: str | Path,
    tokenizer: RobertaTokenizer,
    batch_size: int = 8,
    max_token_length: int = 128,
    num_workers: int = 0,
):
    """
    Devuelve los tres DataLoaders (train, val, test) listos para el entrenamiento.
    """
    train_ds = MultimodalDataset(json_path, "train", tokenizer, max_token_length)
    val_ds   = MultimodalDataset(json_path, "val",   tokenizer, max_token_length)
    test_ds  = MultimodalDataset(json_path, "test",  tokenizer, max_token_length)
    
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,  num_workers=num_workers)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader  = DataLoader(test_ds,  batch_size=batch_size, shuffle=False, num_workers=num_workers)
    
    print(f"  DataLoaders listos:")
    print(f"  train:  {len(train_ds)} ejemplos | {len(train_loader)} batches")
    print(f"  val:    {len(val_ds)} ejemplos | {len(val_loader)} batches")
    print(f"  test:   {len(test_ds)} ejemplos | {len(test_loader)} batches")
    
    return train_loader, val_loader, test_loader


# -----------------------------------------------------------------------
# Test rápido (ejecutar directamente)
# -----------------------------------------------------------------------
if __name__ == "__main__":
    DATASET_PATH = "ml/datasets/dataset.json"
    MODEL_NAME   = "bertin-project/bertin-roberta-base-spanish"
    
    print("Cargando tokenizer...")
    tokenizer = RobertaTokenizer.from_pretrained(MODEL_NAME)
    
    print("Construyendo DataLoaders...")
    train_loader, val_loader, test_loader = get_dataloaders(DATASET_PATH, tokenizer, batch_size=4)
    
    print("\n🔍 Inspeccionando un batch de train:")
    batch = next(iter(train_loader))
    print(f"  pixel_values:   {batch['pixel_values'].shape}")
    print(f"  input_ids:      {batch['input_ids'].shape}")
    print(f"  attention_mask: {batch['attention_mask'].shape}")
    print(f"  labels:         {batch['label']}")
    
    label_names = [IDX_TO_LABEL[l.item()] for l in batch['label']]
    print(f"  categorías:     {label_names}")
    
    print("\n✅ MultimodalDataset funcionando correctamente.")
