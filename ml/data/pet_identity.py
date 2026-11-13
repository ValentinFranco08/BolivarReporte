"""Dataset organizado por identidad: raíz/perro/foto.jpg."""
import hashlib
import random
from pathlib import Path

from PIL import Image, ImageOps
from torch.utils.data import Dataset


def identity_splits(root, seed=42):
    groups = {}
    seen = {}
    for folder in sorted(Path(root).iterdir()):
        if not folder.is_dir() or folder.name.startswith('.'):
            continue
        photos = []
        for path in sorted(folder.iterdir()):
            if path.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
                continue
            digest = hashlib.sha256(path.read_bytes()).digest()
            if digest in seen:
                if seen[digest] != folder.name:
                    raise ValueError(f'Foto duplicada con dos identidades: {path}')
                continue
            seen[digest] = folder.name
            photos.append(path)
        if len(photos) >= 2:
            groups[folder.name] = photos

    identities = sorted(groups)
    if len(identities) < 10:
        raise ValueError('Se requieren al menos 10 perros con dos fotos distintas cada uno.')
    random.Random(seed).shuffle(identities)
    holdout = max(2, len(identities) // 10)
    partitions = (identities[2 * holdout:], identities[:holdout], identities[holdout:2 * holdout])
    return tuple([(path, label) for label in labels for path in groups[label]] for labels in partitions)


class PetIdentityDataset(Dataset):
    def __init__(self, rows, transform):
        self.rows = rows
        self.transform = transform

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        path, identity = self.rows[index]
        with Image.open(path) as photo:
            return self.transform(ImageOps.exif_transpose(photo).convert('RGB')), identity
