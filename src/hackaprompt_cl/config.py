"""Carga de configs/experiment.yaml."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_config(path: str | Path = ROOT / "configs" / "experiment.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
