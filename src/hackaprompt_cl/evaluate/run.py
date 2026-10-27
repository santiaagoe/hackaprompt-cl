"""Ejecuta los ataques sobre el modelo víctima y mide la tasa de éxito (ASR).

Uso (desde la raíz del repo, con GPU o con Ollama):

    python -m hackaprompt_cl.evaluate.run --split pilot --condition en
    python -m hackaprompt_cl.evaluate.run --split pilot --condition en --limit 8   # prueba rápida

Guarda en results/ (o en HACKAPROMPT_RESULTS_DIR):
    <split>_<condition>_<modelo>.parquet   una fila por prompt: respuesta + criterios
    <split>_<condition>_<modelo>.md        tabla de ASR por nivel

Se puede cortar y volver a correr: retoma desde el último lote guardado.
"""

import argparse
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from hackaprompt_cl.config import DATA_DIR, RESULTS_DIR, ROOT, load_config
from hackaprompt_cl.evaluate.success import TARGET, all_criteria
from hackaprompt_cl.evaluate.victim import Victim, load_victim

# Columna con el prompt completo (plantilla + ataque) en cada condición.
CONDITION_COLUMNS = {"en": "prompt", "es_neutro": "prompt_es", "es_cl": "prompt_cl"}
CRITERIA = ("strict", "relaxed", "translated")


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


def score(completion: str, target: str) -> dict[str, bool]:
    """Aplica los tres criterios. El 'traducido' solo aplica a la frase PWNED
    (en el nivel 2 el objetivo es una clave secreta, no una frase traducible)."""
    result = all_criteria(completion, target)
    if target != TARGET:
        result["translated"] = False
    return result


def run_attacks(
    df: pd.DataFrame,
    victim: Victim,
    column: str,
    out_path: Path,
    batch_size: int = 8,
    meta: dict | None = None,
    progress: bool = True,
) -> pd.DataFrame:
    """Envía `df[column]` al modelo por lotes y guarda tras cada lote."""
    done = pd.read_parquet(out_path) if out_path.exists() else pd.DataFrame()
    done_ids = set(done["id"]) if len(done) else set()
    todo = df[~df["id"].isin(done_ids)].reset_index(drop=True)
    if done_ids:
        print(f"Retomando: {len(done_ids)} ya hechos, faltan {len(todo)}.")

    batches = range(0, len(todo), batch_size)
    if progress:
        from tqdm.auto import tqdm

        batches = tqdm(batches, desc=f"{column} → {victim.name}", unit="lote")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    for start in batches:
        chunk = todo.iloc[start : start + batch_size]
        answers = victim.generate(chunk[column].tolist())
        rows = []
        for (_, r), answer in zip(chunk.iterrows(), answers):
            rows.append(
                {
                    "id": r["id"],
                    "level": r["level"],
                    "completion": answer,
                    "expected_completion": r["expected_completion"],
                    **score(answer, r["expected_completion"]),
                    "model": victim.name,
                    **(meta or {}),
                }
            )
        done = pd.concat([done, pd.DataFrame(rows)], ignore_index=True)
        done.to_parquet(out_path, index=False)
    return done


def asr_table(results: pd.DataFrame) -> pd.DataFrame:
    """Tasa de éxito (%) por nivel y total, con los tres criterios."""
    by_level = results.groupby("level")[list(CRITERIA)].mean().mul(100)
    by_level.insert(0, "n", results.groupby("level").size())
    total = pd.DataFrame(
        {"n": [len(results)], **{c: [results[c].mean() * 100] for c in CRITERIA}},
        index=["total"],
    )
    table = pd.concat([by_level, total])
    table.index.name = "nivel"
    return table.round(1)


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--split", default="pilot", choices=["eval", "pilot", "train"])
    parser.add_argument("--condition", default="en", choices=list(CONDITION_COLUMNS))
    parser.add_argument("--input", type=Path, help="parquet de entrada (por defecto, interim)")
    parser.add_argument("--limit", type=int, help="solo los primeros N prompts (prueba)")
    args = parser.parse_args()

    cfg = load_config()
    column = CONDITION_COLUMNS[args.condition]
    in_path = args.input or DATA_DIR / "interim" / f"{args.split}.parquet"
    df = pd.read_parquet(in_path)
    if column not in df.columns:
        raise SystemExit(f"{in_path} no tiene la columna '{column}' (¿falta traducir?).")
    if args.limit:
        df = df.head(args.limit)

    victim = load_victim(cfg)
    out = RESULTS_DIR / f"{args.split}_{args.condition}_{_slug(victim.name)}.parquet"
    meta = {
        "condition": args.condition,
        "commit": _git_commit(),
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    results = run_attacks(df, victim, column, out, cfg["victim"]["batch_size"], meta)

    table = asr_table(results[results["id"].isin(df["id"])])
    report = (
        f"# ASR · {args.split} · {args.condition} · {victim.name}\n\n"
        f"{table.to_markdown()}\n\n"
        f"Tasas en %. Commit `{meta['commit']}`, {meta['run_at']}.\n"
    )
    out.with_suffix(".md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
