"""Filtrado y muestreo estratificado del dataset HackAPrompt."""

import pandas as pd


def filter_dataset(
    df: pd.DataFrame, subset: str, levels: list[int], only_correct: bool
) -> pd.DataFrame:
    """Deja solo la colección, niveles y ataques exitosos pedidos, sin duplicados."""
    out = df[(df["dataset"] == subset) & (df["level"].isin(levels))]
    if only_correct:
        out = out[out["correct"]]
    return out.drop_duplicates(subset=["level", "user_input"]).reset_index(drop=True)


def stratified_sample(df: pd.DataFrame, per_level: int, seed: int) -> pd.DataFrame:
    """Toma `per_level` filas de cada nivel (o todas si hay menos)."""
    parts = [
        g.sample(n=min(per_level, len(g)), random_state=seed)
        for _, g in df.groupby("level", sort=True)
    ]
    return pd.concat(parts).reset_index(drop=True)
