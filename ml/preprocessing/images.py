from PIL import Image
from torchvision import transforms

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

class ImagePreprocessor:
    def __init__(self):
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)), transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])

    def __call__(self, image):
        return self.transform(image)


def smart_animal_crop(image: Image.Image) -> Image.Image:
    """
    Recorta enfocado en el sujeto animal para aislar la mascota y mitigar fondos ruidosos.
    Si la imagen es muy panorámica o vertical, preserva el área central cuadrática.
    """
    w, h = image.size
    if w <= 0 or h <= 0:
        return image
    
    # Si la relación de aspecto es extrema (> 1.5), recortamos hacia el centro
    aspect = max(w, h) / max(min(w, h), 1)
    if aspect > 1.5:
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        image = image.crop((left, top, left + min_dim, top + min_dim))
        w, h = image.size
    
    # Recorte focal centrado (85% central) que concentra el cuerpo y rostro del animal
    left = int(w * 0.075)
    top = int(h * 0.075)
    right = int(w * 0.925)
    bottom = int(h * 0.925)
    return image.crop((left, top, right, bottom))

