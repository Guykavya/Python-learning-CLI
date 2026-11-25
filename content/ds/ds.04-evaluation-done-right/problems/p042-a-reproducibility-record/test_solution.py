import dataclasses
import hashlib
import json

import pandas as pd
import pytest

from conftest import make_churn
from solution import data_fingerprint, run_experiment


@dataclasses.dataclass
class Config:
    name: str = "churn-logreg"
    seed: int = 0
    test_size: float = 0.25
    C: float = 1.0
    features: tuple = ("tenure_months", "monthly_charge", "support_calls", "autopay")


@pytest.fixture(scope="module")
def df():
    return make_churn(n=3000, seed=7)


def test_fingerprint_definition(df):
    h = hashlib.sha256()
    h.update(",".join(map(str, df.columns)).encode())
    h.update(pd.util.hash_pandas_object(df, index=False).to_numpy().tobytes())
    assert data_fingerprint(df) == h.hexdigest()[:16], "SHA-256 of the column names (joined by ',') then the row hashes (index=False); first 16 hex characters."


def test_fingerprint_changes_with_one_cell(df):
    d2 = df.copy()
    d2.loc[0, "tenure_months"] += 1
    assert data_fingerprint(d2) != data_fingerprint(df), "changing one number must change the fingerprint."
    assert data_fingerprint(df.copy()) == data_fingerprint(df), "a copy has the same fingerprint."
    assert data_fingerprint(df.set_index(df.index + 100)) == data_fingerprint(df), "the index is not part of the data (index=False)."


def test_the_same_run_twice_gives_the_same_record(df):
    a = run_experiment(Config(), df)
    b = run_experiment(Config(), df)
    assert a == b, "same configuration and data must give an identical record: seed every random step."
    json.dumps(a)


def test_record_contents(df):
    r = run_experiment(Config(C=0.5), df)
    assert set(r) == {"config", "data", "metrics"}, "record keys: config, data, metrics."
    assert r["config"]["C"] == 0.5 and r["config"]["name"] == "churn-logreg", "config is dataclasses.asdict(cfg)."
    assert r["data"] == {"fingerprint": data_fingerprint(df), "rows": 3000}, "data: fingerprint and number of rows."
    assert 0.6 < r["metrics"]["test_auc"] < 0.85 and 0 < r["metrics"]["test_brier"] < 0.25, "plausible churn metrics."
    assert r["metrics"]["test_auc"] == round(r["metrics"]["test_auc"], 6), "metrics rounded to 6 decimals."


def test_a_different_seed_changes_the_metrics(df):
    assert run_experiment(Config(seed=1), df)["metrics"] != run_experiment(Config(seed=0), df)["metrics"], "the seed controls the split: a different seed gives different test metrics."
