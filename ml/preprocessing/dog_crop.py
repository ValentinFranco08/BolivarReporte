"""Recortar al perro conservando un margen alrededor del cuerpo."""
import torch
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
from torchvision.models.detection import SSDLite320_MobileNet_V3_Large_Weights
from torchvision.transforms.functional import to_tensor


def crop_box(image, box, margin=0.1):
    left, top, right, bottom = box
    x_pad, y_pad = (right - left) * margin, (bottom - top) * margin
    bounds = (max(0, int(left - x_pad)), max(0, int(top - y_pad)),
              min(image.width, int(right + x_pad + 1)), min(image.height, int(bottom + y_pad + 1)))
    if bounds[2] <= bounds[0] or bounds[3] <= bounds[1]:
        return image
    return image.crop(bounds)


class DogCropper:
    def __init__(self, weights, device):
        self.device = device
        self.model = ssdlite320_mobilenet_v3_large(weights=None, weights_backbone=None)
        self.model.load_state_dict(torch.load(weights, map_location="cpu", weights_only=True))
        self.model.to(device).eval()
        self.dog_label = SSDLite320_MobileNet_V3_Large_Weights.DEFAULT.meta["categories"].index("dog")

    @torch.inference_mode()
    def boxes(self, images):
        # Las coordenadas de salida se expresan en las dimensiones de la foto original.
        inputs = [to_tensor(image.resize((320, 320))).to(self.device) for image in images]
        for image, result in zip(images, self.model(inputs)):
            eligible = (result["labels"] == self.dog_label) & (result["scores"] >= 0.45)
            indices = eligible.nonzero().flatten()
            if len(indices) != 1:
                yield None
                continue
            box = result["boxes"][indices[0]].tolist()
            yield tuple(value * scale / 320 for value, scale in zip(box, image.size * 2))
