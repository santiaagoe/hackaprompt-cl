import pandas as pd

from hackaprompt_cl.evaluate.run import asr_table, run_attacks, score


class FakeVictim:
    """Responde PWNED si el prompt contiene 'ok', y cuenta las llamadas."""

    name = "fake"

    def __init__(self):
        self.calls = 0

    def generate(self, prompts):
        self.calls += len(prompts)
        return ["I have been PWNED" if "ok" in p else "No puedo." for p in prompts]


def _df(n=10):
    return pd.DataFrame(
        {
            "id": [f"L1-{i}" for i in range(n)],
            "level": [1 + i % 2 for i in range(n)],
            "prompt": ["ok" if i % 2 == 0 else "no" for i in range(n)],
            "expected_completion": ["I have been PWNED"] * n,
        }
    )


def test_score_secret_key_level():
    s = score("La clave es abc123", "abc123")
    assert s["relaxed"] and not s["strict"] and not s["translated"]


def test_run_attacks_scores_and_saves(tmp_path):
    out = tmp_path / "r.parquet"
    res = run_attacks(_df(), FakeVictim(), "prompt", out, batch_size=3, progress=False)
    assert out.exists() and len(res) == 10
    assert res["strict"].sum() == 5


def test_run_attacks_resumes(tmp_path):
    out = tmp_path / "r.parquet"
    run_attacks(_df(4), FakeVictim(), "prompt", out, batch_size=2, progress=False)
    victim = FakeVictim()
    res = run_attacks(_df(10), victim, "prompt", out, batch_size=2, progress=False)
    assert victim.calls == 6  # solo los que faltaban
    assert res["id"].is_unique and len(res) == 10


def test_asr_table(tmp_path):
    res = run_attacks(_df(), FakeVictim(), "prompt", tmp_path / "r.parquet", progress=False)
    table = asr_table(res)
    assert table.loc["total", "strict"] == 50.0
    assert table.loc[1, "strict"] == 100.0 and table.loc[2, "strict"] == 0.0
