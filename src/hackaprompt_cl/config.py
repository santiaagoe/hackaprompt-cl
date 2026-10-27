"""Carga de configs/experiment.yaml."""

import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

# En Colab se apunta a Drive con HACKAPROMPT_DATA_DIR; en local queda en <repo>/data.
DATA_DIR = Path(os.environ.get("HACKAPROMPT_DATA_DIR", ROOT / "data"))


def load_config(path: str | Path = ROOT / "configs" / "experiment.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
