from dataclasses import dataclass
import torch
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

@dataclass(frozen=True)
class EpochMetrics:
    loss: float
    accuracy: float
    macro_f1: float

    def as_tuple(self):
        return self.loss, self.accuracy, self.macro_f1

class Evaluator:
    def __init__(self, adapter, device, labels):
        self.adapter = adapter
        self.device = device
        self.labels = tuple(labels)

    def evaluate(self, model, loader, criterion, detailed=False):
        model.eval()
        losses, actual, predicted = [], [], []
        with torch.no_grad():
            for batch in loader:
                targets = batch["label"].to(self.device)
                logits = model(**self.adapter.inputs(batch, self.device))
                losses.append(float(criterion(logits, targets).item()))
                actual.extend(targets.cpu().tolist())
                predicted.extend(logits.argmax(dim=-1).cpu().tolist())
        metrics = self.summarize(losses, actual, predicted)
        if not detailed:
            return metrics.as_tuple()
        indices = list(range(len(self.labels)))
        report = classification_report(actual, predicted, labels=indices,
            target_names=self.labels, digits=4, zero_division=0)
        return (*metrics.as_tuple(), report, confusion_matrix(actual, predicted, labels=indices))

    @staticmethod
    def summarize(losses, actual, predicted):
        if not actual:
            raise ValueError("El DataLoader no contiene muestras")
        return EpochMetrics(sum(losses) / len(losses), accuracy_score(actual, predicted),
            f1_score(actual, predicted, average="macro", zero_division=0))

