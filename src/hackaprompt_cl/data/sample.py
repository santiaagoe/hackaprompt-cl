"""Limpieza del dataset HackAPrompt y división en muestras disjuntas.

Flujo:
    raw ─clean_pool─▶ pool (un prompt único por nivel) ─split_by_level─▶ eval / pilot / train

- eval:  muestra principal del experimento (por defecto 125 por nivel).
- pilot: para ajustar la traducción antes de escalar (10 por nivel).
- train: pares para entrenar el traductor propio, opción C (100 por nivel).

Un mismo prompt nunca queda en dos muestras, para que lo usado en el piloto o
en el entrenamiento del traductor no contamine la evaluación.
"""

import hashlib
import re
import warnings

import numpy as np
import pandas as pd

SPLITS = ("eval", "pilot", "train")

OUTPUT_COLUMNS = [
    "id",
    "level",
    "user_input",
    "prompt",
    "expected_completion",
    "token_count",
    "models",
    "n_models",
    "split",
]


def normalize_text(text: str) -> str:
    """Clave para detectar duplicados: minúsculas y espacios colapsados."""
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def _as_bool(series: pd.Series) -> pd.Series:
    """`correct` puede venir como bool o como texto según la versión del dataset."""
    if series.dtype == bool:
        return series
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def make_id(level: int, normalized: str) -> str:
    """Id estable: el mismo prompt recibe el mismo id en cualquier computador."""
    digest = hashlib.sha1(f"{level}|{normalized}".encode()).hexdigest()[:10]
    return f"L{int(level)}-{digest}"


def clean_pool(
    df: pd.DataFrame,
    subset: str,
    levels: list[int],
    only_correct: bool = True,
    max_token_count: int | None = None,
) -> pd.DataFrame:
    """Filtra y deja un solo registro por (nivel, prompt normalizado).

    Si el mismo ataque funcionó en varios modelos se guarda la lista en `models`
    y su cantidad en `n_models`, que sirve como medida de cuán "transferible" es.
    """
    out = df[(df["dataset"] == subset) & (df["level"].isin(levels))].copy()
    if only_correct:
        out = out[_as_bool(out["correct"])]
    out = out[out["user_input"].notna()]
    out["_norm"] = out["user_input"].map(normalize_text)
    out = out[out["_norm"] != ""]
    if max_token_count is not None:
        out = out[out["token_count"] <= max_token_count]

    models = (
        out.groupby(["level", "_norm"])["model"]
        .agg(lambda m: ",".join(sorted(set(map(str, m)))))
        .rename("models")
    )
    # Representante determinista: el de menos tokens (como en el ranking de la
    # competencia) y, en empate, el primero alfabéticamente.
    out = out.sort_values(["level", "_norm", "token_count", "user_input"])
    out = out.drop_duplicates(["level", "_norm"]).join(models, on=["level", "_norm"])
    out["n_models"] = out["models"].str.count(",") + 1
    out["id"] = [make_id(lv, n) for lv, n in zip(out["level"], out["_norm"])]
    return out.drop(columns="_norm").reset_index(drop=True)


def split_by_level(pool: pd.DataFrame, sizes: dict[str, int], seed: int) -> pd.DataFrame:
    """Asigna cada prompt a una muestra (`split`), por nivel y sin solapamiento.

    `sizes` es el tamaño por nivel de cada muestra, en orden de prioridad:
    si un nivel tiene pocos prompts se llena primero eval, luego pilot, luego train.
    Los prompts que sobran no se asignan.
    """
    rng = np.random.default_rng(seed)
    parts = []
    for level, group in pool.sort_values("id").groupby("level", sort=True):
        order = rng.permutation(len(group))
        shuffled = group.iloc[order]
        start = 0
        for name in SPLITS:
            want = sizes.get(name, 0)
            chunk = shuffled.iloc[start : start + want].assign(split=name)
            if len(chunk) < want:
                warnings.warn(
                    f"Nivel {level}: se pidieron {want} para '{name}' y solo quedan {len(chunk)}.",
                    stacklevel=2,
                )
            parts.append(chunk)
            start += len(chunk)
    result = pd.concat(parts, ignore_index=True)
    return result[OUTPUT_COLUMNS]


def summary(raw: pd.DataFrame, pool: pd.DataFrame, assigned: pd.DataFrame) -> str:
    """Reporte en Markdown con los conteos de cada paso, para el issue y el informe."""
    counts = (
        assigned.pivot_table(index="level", columns="split", values="id", aggfunc="count")
        .reindex(columns=list(SPLITS))
        .fillna(0)
        .astype(int)
    )
    counts.insert(0, "disponibles", pool.groupby("level").size())
    counts.loc["total"] = counts.sum()

    tokens = assigned.groupby("split")["token_count"].describe(percentiles=[0.5, 0.9])
    tokens = tokens.reindex(list(SPLITS))[["count", "mean", "50%", "90%", "max"]].round(1)

    lines = [
        "# Reporte de muestreo",
        "",
        f"- Filas en el dataset original: {len(raw):,}",
        f"- Prompts únicos tras filtrar y deduplicar: {len(pool):,}",
        f"- Prompts asignados: {len(assigned):,}",
        "",
        "## Prompts por nivel y muestra",
        "",
        counts.to_markdown(),
        "",
        "## Largo en tokens por muestra",
        "",
        tokens.to_markdown(),
        "",
        "## Modelos en que funcionó cada ataque (muestra eval)",
        "",
        assigned[assigned["split"] == "eval"]["n_models"]
        .value_counts()
        .sort_index()
        .rename_axis("n_models")
        .rename("prompts")
        .to_frame()
        .to_markdown(),
        "",
    ]
    return "\n".join(lines)
