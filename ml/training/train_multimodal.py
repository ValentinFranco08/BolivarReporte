"""Entrada compatible; el entrenamiento reside en ExperimentRunner y Trainer."""
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.training.experiment import training_main


def main():
    training_main("multimodal")


if __name__ == "__main__":
    main()
