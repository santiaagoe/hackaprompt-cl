import pandas as pd

from hackaprompt_cl.data.sample import filter_dataset, stratified_sample


def _toy():
    rows = []
    for level in (1, 2, 9):
        for i in range(20):
            rows.append(
                {
                    "dataset": "submission_data",
                    "level": level,
                    "correct": i % 2 == 0,
                    "user_input": f"ataque {i % 15}",
                }
            )
    return pd.DataFrame(rows)


def test_filter_excludes_levels_and_failures():
    out = filter_dataset(_toy(), "submission_data", [1, 2], only_correct=True)
    assert set(out["level"]) == {1, 2}
    assert out["correct"].all()
    assert not out.duplicated(["level", "user_input"]).any()


def test_stratified_sample_is_reproducible():
    df = filter_dataset(_toy(), "submission_data", [1, 2], only_correct=True)
    a = stratified_sample(df, per_level=3, seed=13)
    b = stratified_sample(df, per_level=3, seed=13)
    assert a.equals(b)
    assert (a["level"].value_counts() == 3).all()
