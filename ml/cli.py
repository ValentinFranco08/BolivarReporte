"""Ejecutar desde la raíz: python -m ml.cli --help."""
import argparse
import json
from pathlib import Path

def main(argv=None):
    parser = argparse.ArgumentParser(description="Herramientas de ML Bolívar Animal")
    commands = parser.add_subparsers(dest="command", required=True)
    train = commands.add_parser("train")
    train.add_argument("--model", choices=("vit", "roberta", "multimodal"), default="multimodal")
    predict = commands.add_parser("predict")
    predict.add_argument("--image", required=True)
    predict.add_argument("--text", default="")
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("--model", choices=("vit", "roberta", "multimodal"), default="multimodal")
    evaluate.add_argument("--config")
    evaluate.add_argument("--checkpoint", required=True)
    prepare = commands.add_parser("prepare-data")
    prepare.add_argument("--source", required=True)
    prepare.add_argument("--output")
    prepare.add_argument("--per-class", type=int)
    prepare.add_argument("--image-root", default=".")
    commands.add_parser("incremental")
    args, remaining = parser.parse_known_args(argv)
    if args.command == "train":
        from ml.training.experiment import training_main
        return training_main(args.model, remaining)
    if args.command == "incremental":
        from ml.training.train_incremental import main as incremental
        return incremental(remaining)
    if remaining:
        parser.error(f"Argumentos desconocidos: {' '.join(remaining)}")
    if args.command == "predict":
        from ml.inference.predictor import MultimodalPredictor
        result = MultimodalPredictor().predict(Path(args.image).read_bytes(), args.text)
    elif args.command == "prepare-data":
        from ml.data.preparation import DatasetPreparation
        result = DatasetPreparation().run(args.source, args.output, args.per_class, Path(args.image_root))
    else:
        from ml.training.experiment import ExperimentRunner, load_config
        from ml.training.engine import ADAPTERS, Evaluator
        from ml.device import get_device
        runner = ExperimentRunner(args.model, load_config(args.model, args.config))
        device = get_device()
        artifact = runner.checkpoints.load(args.checkpoint, device)
        from ml.taxonomy import IDX_TO_LABEL
        if artifact.labels != tuple(IDX_TO_LABEL[i] for i in sorted(IDX_TO_LABEL)):
            raise ValueError("El checkpoint utiliza una taxonomía diferente a la del dataset")
        model = runner.create_model().to(device)
        model.load_state_dict(artifact.state_dict)
        loss, accuracy, f1, report, matrix = Evaluator(ADAPTERS[args.model](), device, artifact.labels).evaluate(
            model, runner.create_loaders()[2], runner.criterion().to(device), detailed=True)
        result = {"loss": loss, "accuracy": accuracy, "macro_f1": f1,
                  "classification_report": report, "confusion_matrix": matrix.tolist()}
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
