"""Ciclo común de entrenamiento; variación de entradas mediante polimorfismo."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import torch
from ml.evaluation.evaluator import EpochMetrics, Evaluator
from ml.inference.checkpoints import CheckpointLoader

class BatchAdapter(ABC):
    @abstractmethod
    def inputs(self, batch, device):
        """Selecciona y mueve a dispositivo las entradas propias del modelo."""

class ImageBatchAdapter(BatchAdapter):
    def inputs(self, batch, device):
        return {"pixel_values": batch["pixel_values"].to(device)}

class TextBatchAdapter(BatchAdapter):
    def inputs(self, batch, device):
        return {key: batch[key].to(device) for key in ("input_ids", "attention_mask")}

class MultimodalBatchAdapter(BatchAdapter):
    def inputs(self, batch, device):
        return {key: batch[key].to(device) for key in ("pixel_values", "input_ids", "attention_mask")}

ADAPTERS = {"vit": ImageBatchAdapter, "roberta": TextBatchAdapter, "multimodal": MultimodalBatchAdapter}

@dataclass(frozen=True)
class TrainingPhase:
    name: str
    epochs: int
    unfreeze: tuple[tuple[str, int], ...] = ()

    def prepare(self, model):
        for component, count in self.unfreeze:
            if count > 0:
                getattr(model, component).unfreeze_last_n_layers(count)

class Trainer:
    def __init__(self, model, adapter, criterion, device, labels, config=None, checkpoints=None):
        self.model = model
        self.adapter = adapter
        self.criterion = criterion
        self.device = device
        self.labels = tuple(labels)
        self.config = dict(config or {})
        self.checkpoints = checkpoints or CheckpointLoader()
        self.evaluator = Evaluator(adapter, device, self.labels)

    def train_epoch(self, loader, optimizer, grad_clip=1.0):
        self.model.train()
        losses, actual, predicted = [], [], []
        for batch in loader:
            targets = batch["label"].to(self.device)
            optimizer.zero_grad()
            logits = self.model(**self.adapter.inputs(batch, self.device))
            loss = self.criterion(logits, targets)
            loss.backward()
            if grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), grad_clip)
            optimizer.step()
            losses.append(float(loss.item()))
            actual.extend(targets.cpu().tolist())
            predicted.extend(logits.argmax(dim=-1).cpu().tolist())
        return self.evaluator.summarize(losses, actual, predicted).as_tuple()

    def run_phase(self, train_loader, val_loader, optimizer, scheduler, phase,
                  checkpoint_dir, patience=5, grad_clip=1.0):
        if phase.epochs < 1:
            raise ValueError("Cada fase debe tener al menos una época")
        best_f1, stale, history = -1.0, 0, []
        path = Path(checkpoint_dir) / f"best_{phase.name}.pt"
        for epoch in range(1, phase.epochs + 1):
            train = self.train_epoch(train_loader, optimizer, grad_clip)
            val = self.evaluator.evaluate(self.model, val_loader, self.criterion)
            if scheduler is not None:
                scheduler.step()
            row = dict(epoch=epoch, phase=phase.name, train_loss=train[0], train_acc=train[1],
                       train_f1=train[2], val_loss=val[0], val_acc=val[1], val_f1=val[2])
            history.append(row)
            print(f"{phase.name} {epoch}/{phase.epochs}: loss={train[0]:.4f} val_f1={val[2]:.4f}")
            if val[2] > best_f1:
                best_f1, stale = val[2], 0
                self.checkpoints.save(path, self.model, labels=self.labels, config=self.config,
                    optimizer=optimizer, scheduler=scheduler, epoch=epoch, metrics=row)
            else:
                stale += 1
                if stale >= patience:
                    break
        return history, best_f1, path
