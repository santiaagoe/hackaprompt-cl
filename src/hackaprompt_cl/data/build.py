"""Etapa 1 completa: descargar, limpiar y dividir el dataset.

Uso (desde la raíz del repo):

    python -m hackaprompt_cl.data.build            # descarga si falta y genera las muestras
    python -m hackaprompt_cl.data.build --force    # vuelve a descargar

Genera en data/interim/:
    pool.parquet         todos los prompts únicos que pasaron los filtros
    eval.parquet         muestra principal (1.000)
    pilot.parquet/.csv   piloto de traducción (80); el CSV se abre en Sheets/Excel
    train.parquet        pares para entrenar el traductor propio (800)
    sample_report.md     conteos para pegar en el issue y en el informe
"""

import argparse
import subprocess

import pandas as pd

from hackaprompt_cl.config import DATA_DIR, ROOT, load_config
from hackaprompt_cl.data.download import RAW_PATH, download
from hackaprompt_cl.data.sample import SPLITS, clean_pool, split_by_level, summary

INTERIM = DATA_DIR / "interim"


def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconocido"


def build(force_download: bool = False) -> pd.DataFrame:
    cfg = load_config()
    ds = cfg["dataset"]

    download(ds["hf_name"], RAW_PATH, force=force_download)
    raw = pd.read_parquet(RAW_PATH)

    pool = clean_pool(
        raw,
        subset=ds["subset"],
        levels=ds["levels"],
        only_correct=ds["only_correct"],
        max_token_count=ds.get("max_token_count"),
    )
    sizes = {
        "eval": ds["per_level"],
        "pilot": ds["pilot_per_level"],
        "train": ds["train_per_level"],
    }
    assigned = split_by_level(pool, sizes, seed=cfg["seed"])

    INTERIM.mkdir(parents=True, exist_ok=True)
    pool.to_parquet(INTERIM / "pool.parquet", index=False)
    for name in SPLITS:
        part = assigned[assigned["split"] == name].reset_index(drop=True)
        part.to_parquet(INTERIM / f"{name}.parquet", index=False)
    pilot = assigned[assigned["split"] == "pilot"]
    pilot.to_csv(INTERIM / "pilot.csv", index=False, encoding="utf-8-sig")

    report = summary(raw, pool, assigned)
    report += f"\nGenerado con el commit `{_git_commit()}` y semilla {cfg['seed']}.\n"
    (INTERIM / "sample_report.md").write_text(report, encoding="utf-8")
    print(report)
    return assigned


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="volver a descargar el dataset")
    args = parser.parse_args()
    build(force_download=args.force)


if __name__ == "__main__":
    main()
