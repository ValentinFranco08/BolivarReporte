"""Pesos y metadatos versionados; lectura compatible con state_dict históricos."""
from dataclasses import dataclass
from pathlib import Path
import torch
from ml.taxonomy import IDX_TO_LABEL

@dataclass(frozen=True)
class ModelArtifact:
    state_dict: dict
    labels: tuple[str, ...]
    config: dict
    metadata: dict

    @property
    def num_classes(self):
        return len(self.labels)

class CheckpointLoader:
    def load(self, path, device="cpu", legacy_labels=None) -> ModelArtifact:
        payload = torch.load(path, map_location=device, weights_only=True)
        state = payload.get("model_state_dict", payload)
        classifier_weights = {key: value for key, value in state.items()
                              if key.startswith("classifier.") and key.endswith(".weight")}
        if not classifier_weights:
            raise ValueError("El checkpoint no contiene una cabeza clasificadora reconocida")
        last_key = max(classifier_weights, key=lambda key: int(key.split(".")[1]))
        count = int(classifier_weights[last_key].shape[0])
        labels = payload.get("labels", legacy_labels)
        if labels is None:
            if count != len(IDX_TO_LABEL):
                raise ValueError("Checkpoint sin etiquetas y con otra dimensión: proporcionar legacy_labels explícitas")
            labels = [IDX_TO_LABEL[i] for i in range(count)]
        labels = tuple(labels)
        if len(labels) != count or len(set(labels)) != count:
            raise ValueError("Las etiquetas del checkpoint no coinciden con la cabeza clasificadora")
        return ModelArtifact(state, labels, payload.get("config", {}),
                             payload.get("metadata", {}))

    def save(self, path, model, *, labels=None, config=None, optimizer=None,
             scheduler=None, epoch=0, metrics=None):
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "format_version": 1,
            "model_state_dict": model.state_dict(),
            "labels": list(labels) if labels is not None else [IDX_TO_LABEL[i] for i in sorted(IDX_TO_LABEL)],
            "config": dict(config or {}),
            "metadata": {"epoch": epoch, "metrics": dict(metrics or {}),
                         "preprocessing_version": "imagenet-224-text-128-v1"},
        }
        if optimizer is not None:
            payload["optimizer_state_dict"] = optimizer.state_dict()
        if scheduler is not None:
            payload["scheduler_state_dict"] = scheduler.state_dict()
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        torch.save(payload, temporary)
        temporary.replace(destination)

    def restore_training(self, path, model, optimizer=None, scheduler=None, device="cpu"):
        artifact = self.load(path, device)
        model.load_state_dict(artifact.state_dict)
        payload = torch.load(path, map_location=device, weights_only=True)
        if optimizer is not None and "optimizer_state_dict" in payload:
            optimizer.load_state_dict(payload["optimizer_state_dict"])
        if scheduler is not None and "scheduler_state_dict" in payload:
            scheduler.load_state_dict(payload["scheduler_state_dict"])
        return artifact
