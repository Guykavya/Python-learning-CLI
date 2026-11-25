import numpy as np
import pytest
from sklearn.linear_model import LinearRegression, LogisticRegression

from solution import beats_baseline


def reg_data(seed, signal, n_tr=40, n_te=400, k=20):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n_tr + n_te, k))
    y = (3 * X[:, 0] if signal else 0) + rng.normal(size=n_tr + n_te)
    return X[:n_tr], y[:n_tr], X[n_tr:], y[n_tr:]


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_real_signal_beats_the_baseline(seed):
    m, b, beats = beats_baseline(LinearRegression(), *reg_data(seed, True), "regression")
    assert beats is True and m < b, "a linear model on data with a strong linear signal must beat the mean baseline on test rows."
    assert b > 2.5, "the baseline RMSE is about the spread of y (about 3.2)."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_pure_noise_does_not_beat_the_baseline(seed):
    m, b, beats = beats_baseline(LinearRegression(), *reg_data(seed, False), "regression")
    assert beats is False, f"20 noise features and 40 rows: the model memorises noise (RMSE {m:.2f} vs baseline {b:.2f}) and must not beat the baseline. Score on the TEST rows."


def test_classification_majority_baseline():
    rng = np.random.default_rng(3)
    X = rng.normal(size=(600, 3))
    y = (rng.random(600) < 0.9).astype(int)           # 90% ones, pure noise
    m, b, beats = beats_baseline(LogisticRegression(), X[:300], y[:300], X[300:], y[300:], "classification")
    assert b == pytest.approx(float(np.mean(y[300:] == 1)), abs=1e-12), "the baseline predicts the most frequent TRAINING class (1) for every test row."
    assert beats is False, "a model that cannot do better than always saying 1 has not beaten the baseline (use strict >)."


def test_classification_real_signal():
    rng = np.random.default_rng(4)
    X = rng.normal(size=(600, 3))
    y = (X[:, 0] + 0.3 * rng.normal(size=600) > 0).astype(int)
    m, b, beats = beats_baseline(LogisticRegression(), X[:300], y[:300], X[300:], y[300:], "classification")
    assert beats is True and m > 0.8, "with a clear signal the accuracy should be far above the majority-class share."


def test_types_and_unknown_task():
    m, b, beats = beats_baseline(LinearRegression(), *reg_data(0, True), "regression")
    assert isinstance(m, float) and isinstance(b, float) and isinstance(beats, bool), "return plain floats and a plain bool."
    with pytest.raises(ValueError):
        beats_baseline(LinearRegression(), *reg_data(0, True), "ranking")
