import json
from pathlib import Path
import pytest
import torch
from torch import nn
from torch.utils.data import DataLoader
from ml.inference.checkpoints import CheckpointLoader
from ml.training.trainer import Trainer
from ml.training.incremental import IncrementalTrainer
from ml.evaluation.evaluator import Evaluator
from ml.data.preparation import DatasetValidator, DatasetPreparation
from ml.training.train import training_main
from ml.taxonomy import IDX_TO_LABEL

class TinyClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.classifier = nn.Sequential(nn.Linear(4, 2))

    def forward(self, pixel_values):
        return self.classifier(pixel_values)


def test_training_checkpoint_and_resume_roundtrip(tmp_path):
    torch.manual_seed(42)
    model = TinyClassifier()
    dataset = [{"pixel_values": torch.tensor([1., 0, 0, 0]), "label": torch.tensor(0)},
               {"pixel_values": torch.tensor([0., 1, 0, 0]), "label": torch.tensor(1)}]
    loader = DataLoader(dataset, batch_size=2)
    optimizer = torch.optim.AdamW(model.parameters(), lr=.1)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1)
    trainer = Trainer(model, nn.CrossEntropyLoss(), torch.device("cpu"), ("a", "b"))
    before = model.classifier[0].weight.detach().clone()
    history, _, path = trainer.fit(loader, loader, optimizer, scheduler,
                                         2, tmp_path, phase_name="tiny")
    assert not torch.equal(before, model.classifier[0].weight)
    assert len(history) == 2 and path.is_file()
    restored = TinyClassifier()
    restored_optimizer = torch.optim.AdamW(restored.parameters(), lr=.1)
    artifact = CheckpointLoader().restore_training(path, restored, restored_optimizer, device="cpu")
    assert artifact.labels == ("a", "b")
    assert restored_optimizer.state_dict()["state"]
    expected = trainer.checkpoints.load(path)
    assert torch.equal(restored.classifier[0].weight, expected.state_dict["classifier.0.weight"])


def test_zero_f1_still_creates_a_checkpoint(tmp_path):
    model = TinyClassifier()
    with torch.no_grad():
        model.classifier[0].weight.zero_()
        model.classifier[0].bias.copy_(torch.tensor([1., 0.]))
    loader = DataLoader([{"pixel_values": torch.zeros(4), "label": torch.tensor(1)}])
    trainer = Trainer(model, nn.CrossEntropyLoss(), "cpu", ("a", "b"))
    _, f1, path = trainer.fit(loader, loader, torch.optim.SGD(model.parameters(), lr=0),
                                    None, 1, tmp_path, phase_name="zero")
    assert f1 == 0 and path.is_file()


def test_legacy_checkpoint_and_metadata_validation(tmp_path):
    model = TinyClassifier()
    path = tmp_path / "legacy.pt"
    torch.save(model.state_dict(), path)
    with pytest.raises(ValueError, match="legacy_labels"):
        CheckpointLoader().load(path)
    artifact = CheckpointLoader().load(path, legacy_labels=("a", "b"))
    assert artifact.num_classes == 2
    assert artifact.labels == ("a", "b")
    CheckpointLoader().save(path, model, labels=["one"])
    with pytest.raises(ValueError, match="etiquetas"):
        CheckpointLoader().load(path)


@pytest.mark.parametrize("kind", ["vit", "roberta", "multimodal"])
def test_same_trainer_accepts_image_text_and_multimodal_models(kind, tmp_path):
    class ImageModel(TinyClassifier):
        def forward(self, pixel_values, **kwargs):
            return self.classifier(pixel_values)

    class TextModel(TinyClassifier):
        def forward(self, input_ids, attention_mask, **kwargs):
            return self.classifier(input_ids.float() * attention_mask)

    class MultimodalModel(TinyClassifier):
        def forward(self, pixel_values, input_ids, attention_mask):
            return self.classifier(pixel_values + input_ids.float() * attention_mask)

    models = {"vit": ImageModel, "roberta": TextModel, "multimodal": MultimodalModel}
    model = models[kind]()
    batch = {"pixel_values": torch.ones(4), "input_ids": torch.ones(4, dtype=torch.long),
             "attention_mask": torch.ones(4), "label": torch.tensor(0)}
    loader = DataLoader([batch])
    trainer = Trainer(model, nn.CrossEntropyLoss(), "cpu", ("a", "b"))
    result = trainer.train_epoch(loader, torch.optim.SGD(model.parameters(), lr=.01))
    assert all(__import__("math").isfinite(value) for value in result)
    assert len(trainer.evaluator.evaluate(model, loader, trainer.criterion)) == 3


def test_detailed_evaluation_handles_absent_classes():
    model = TinyClassifier()
    loader = DataLoader([{"pixel_values": torch.zeros(4), "label": torch.tensor(0)}])
    result = Evaluator("cpu", ("a", "b")).evaluate(model, loader, nn.CrossEntropyLoss(), detailed=True)
    assert result[-1].shape == (2, 2)
    with pytest.raises(ValueError, match="muestras"):
        Evaluator("cpu", ("a", "b")).evaluate(model, [], nn.CrossEntropyLoss())


def test_incremental_replay_uses_only_train_and_dry_run_does_not_load_weights(tmp_path):
    image = tmp_path / "pet.jpg"
    image.write_bytes(b"image")
    label = IDX_TO_LABEL[0]
    samples = [{"image": str(image), "text": "Animal", "label": label, "feedback_id": 9}]
    historical = [{"image": str(image), "text": "Histórico", "label": label, "split": "train"},
                  {"image": str(image), "text": "Test", "label": label, "split": "test"}]
    trainer = IncrementalTrainer(model_factory=lambda: pytest.fail("No debe cargar el modelo"))
    result = trainer.run(samples, historical, "missing.pt", tmp_path / "new.pt", dry_run=True)
    assert result == {"feedback_ids": [9], "corrections": 1, "replay": 1, "saved": False}
    assert not (tmp_path / "new.pt").exists()
    with pytest.raises(ValueError, match="históricas"):
        trainer.prepare(samples, historical[1:])


def test_dataset_validation_and_balance_preserve_evaluation_splits(tmp_path):
    image = tmp_path / "pet.jpg"
    image.write_bytes(b"image")
    label = IDX_TO_LABEL[0]
    records = [{"image": str(image), "text": "Animal", "label": label, "split": "train"}]
    assert DatasetValidator().validate(records) == []
    leak = records + [{**records[0], "split": "test"}]
    assert any("splits" in error for error in DatasetValidator().validate(leak))
    balanced = DatasetPreparation().balance_train(records * 4, 2)
    assert len(balanced) == 2


def test_cli_training_dry_run_does_not_construct_models(capsys):
    training_main("multimodal", ["--dry-run", "--epochs-phase1", "1"])
    result = json.loads(capsys.readouterr().out)
    assert result["config"]["epochs_phase1"] == 1
    assert result["phases"] == ["fase1", "fase2", "fase3"]


def test_full_training_workflow_runs_all_phases_and_saves_final_artifact(tmp_path, monkeypatch):
    from ml.training import train
    model = TinyClassifier()
    model.classifier = nn.Sequential(nn.Linear(4, len(IDX_TO_LABEL)))
    loader = DataLoader([{"pixel_values": torch.ones(4), "label": torch.tensor(0)},
                         {"pixel_values": torch.zeros(4), "label": torch.tensor(1)}], batch_size=2)
    monkeypatch.setattr(train, "create_model", lambda kind: model)
    monkeypatch.setattr(train, "create_loaders", lambda config: (loader, loader, loader))
    monkeypatch.setattr(train, "create_loss", lambda kind, config: nn.CrossEntropyLoss())
    monkeypatch.setattr(train, "get_device", lambda: torch.device("cpu"))
    config = train.load_config("multimodal")
    config.update(checkpoint_dir=str(tmp_path), epochs_phase1=1, epochs_phase2=1,
                  epochs_phase3=1, unfreeze_vit_layers=0, unfreeze_roberta_layers=0)
    result = train.run_training("multimodal", config)
    assert [row["phase"] for row in result["history"]] == ["fase1", "fase2", "fase3"]
    artifact = CheckpointLoader().load(tmp_path / "best_multimodal_finetuned.pt")
    assert artifact.labels == tuple(IDX_TO_LABEL[i] for i in sorted(IDX_TO_LABEL))
    assert (tmp_path / "results.json").is_file()
