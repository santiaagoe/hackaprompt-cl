"""Carga de configs/experiment.yaml."""

import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

# En Colab se apuntan a Drive con estas variables; en local quedan dentro del repo.
DATA_DIR = Path(os.environ.get("HACKAPROMPT_DATA_DIR", ROOT / "data"))
RESULTS_DIR = Path(os.environ.get("HACKAPROMPT_RESULTS_DIR", ROOT / "results"))


def load_config(path: str | Path = ROOT / "configs" / "experiment.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
