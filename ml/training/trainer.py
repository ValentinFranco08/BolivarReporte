"""Trainer: aprendizaje por lotes, validación y guardado del mejor modelo."""
from pathlib import Path
import torch
from ml.evaluation.evaluator import Evaluator
from ml.inference.checkpoints import CheckpointLoader

class Trainer:
    def __init__(self, model, criterion, device, labels, config=None, checkpoints=None):
        self.model = model
        self.criterion = criterion
        self.device = device
        self.labels = tuple(labels)
        self.config = dict(config or {})
        self.checkpoints = checkpoints or CheckpointLoader()
        self.evaluator = Evaluator(device, self.labels)

    def train_epoch(self, loader, optimizer, grad_clip=1.0):
        """Recorre los lotes y actualiza los pesos entrenables del modelo."""
        self.model.train()
        losses, actual, predicted = [], [], []
        for batch in loader:
            targets = batch["label"].to(self.device)
            optimizer.zero_grad()
            inputs = {name: value.to(self.device) for name, value in batch.items() if name != "label"}
            logits = self.model(**inputs)
            loss = self.criterion(logits, targets)
            loss.backward()
            if grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), grad_clip)
            optimizer.step()
            losses.append(float(loss.item()))
            actual.extend(targets.cpu().tolist())
            predicted.extend(logits.argmax(dim=-1).cpu().tolist())
        return self.evaluator.summarize(losses, actual, predicted).as_tuple()

    def fit(self, train_loader, val_loader, optimizer, scheduler, epochs,
            checkpoint_dir, phase_name="training", patience=5, grad_clip=1.0):
        """Entrena una fase, valida cada época y guarda su mejor checkpoint."""
        if epochs < 1:
            raise ValueError("Cada fase debe tener al menos una época")
        best_f1, stale, history = -1.0, 0, []
        path = Path(checkpoint_dir) / f"best_{phase_name}.pt"
        for epoch in range(1, epochs + 1):
            train = self.train_epoch(train_loader, optimizer, grad_clip)
            val = self.evaluator.evaluate(self.model, val_loader, self.criterion)
            if scheduler is not None:
                scheduler.step()
            row = dict(epoch=epoch, phase=phase_name, train_loss=train[0], train_acc=train[1],
                       train_f1=train[2], val_loss=val[0], val_acc=val[1], val_f1=val[2])
            history.append(row)
            print(f"{phase_name} {epoch}/{epochs}: loss={train[0]:.4f} val_f1={val[2]:.4f}")
            if val[2] > best_f1:
                best_f1, stale = val[2], 0
                self.checkpoints.save(path, self.model, labels=self.labels, config=self.config,
                    optimizer=optimizer, scheduler=scheduler, epoch=epoch, metrics=row)
            else:
                stale += 1
                if stale >= patience:
                    break
        return history, best_f1, path
