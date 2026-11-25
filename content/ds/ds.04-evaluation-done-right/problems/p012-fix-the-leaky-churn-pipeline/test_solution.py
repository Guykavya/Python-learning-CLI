import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

from conftest import RecordingScaler, make_churn
from solution import churn_auc


def train_rows(df, seed):
    X = pd.get_dummies(df.drop(columns=["churned", "retention_offer_sent"]), dtype=float)
    y = df["churned"].to_numpy()
    Xa, Xb, _, _ = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    return {row.tobytes() for row in Xa.to_numpy(dtype=float)}, len(Xa), X.shape[1]


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_the_scaler_sees_only_training_rows(seed):
    df = make_churn(seed=seed, leaks=True)
    RecordingScaler.log.clear()
    churn_auc(df, seed=seed, scaler_cls=RecordingScaler)
    assert len(RecordingScaler.log) == 1, "fit the scaler exactly once (inside the pipeline), using scaler_cls()."
    fitted = RecordingScaler.log[0]
    rows, n_train, n_cols = train_rows(df, seed)
    assert len(fitted) == n_train, f"your scaler was fitted on {len(fitted)} rows; it must see only the {n_train} training rows. Split first."
    assert all(len(r) == 8 * n_cols for r in fitted), f"the scaler should see {n_cols} feature columns: drop retention_offer_sent (written after the outcome)."
    assert set(fitted) <= rows, "your scaler saw rows that are not in the training set: split BEFORE fitting anything."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_the_honest_score(seed):
    auc = churn_auc(make_churn(seed=seed, leaks=True), seed=seed)
    assert 0.70 < auc < 0.82, f"AUC {auc:.3f}: the honest churn AUC is about 0.74-0.78. Above 0.9 means the post-outcome column is still in."


def test_works_without_the_leaky_column():
    auc = churn_auc(make_churn(seed=0, leaks=False), seed=0)
    assert 0.70 < auc < 0.82, "the function must also work on data that never had the leaky column."
