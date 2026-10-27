"""Descarga del dataset HackAPrompt desde Hugging Face.

El dataset es público pero con acceso condicionado: antes de correr esto hay que
aceptar sus condiciones en https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset
y tener `HF_TOKEN` en el entorno (o en `.env`, o en los Secrets de Colab).
"""

import os
from pathlib import Path

import pandas as pd

from hackaprompt_cl.config import DATA_DIR, ROOT

RAW_PATH = DATA_DIR / "raw" / "hackaprompt.parquet"


def _load_dotenv() -> None:
    """Lee `.env` si existe, sin depender de python-dotenv."""
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            value = value.strip().strip("'\"")
            if value:
                os.environ.setdefault(key.strip(), value)


def download(hf_name: str, out_path: Path = RAW_PATH, force: bool = False) -> Path:
    """Descarga el dataset completo a `data/raw/` como parquet (unos 150 MB).

    Si el archivo ya existe no vuelve a descargar, salvo que `force=True`.
    """
    if out_path.exists() and not force:
        print(f"Ya existe {out_path}, no se descarga de nuevo.")
        return out_path

    from datasets import load_dataset  # import local: solo se necesita al descargar

    _load_dotenv()
    # strip(): un token copiado con un espacio o salto de línea al final hace fallar
    # la conexión con "Illegal header value"
    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "Falta HF_TOKEN. Créalo en https://huggingface.co/settings/tokens, acepta las "
            "condiciones del dataset y guárdalo en .env o en los Secrets de Colab."
        )

    splits = load_dataset(hf_name, token=token)  # DatasetDict; se juntan todos los splits
    df = pd.concat([s.to_pandas() for s in splits.values()], ignore_index=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    print(f"Descargadas {len(df):,} filas en {out_path}")
    return out_path
