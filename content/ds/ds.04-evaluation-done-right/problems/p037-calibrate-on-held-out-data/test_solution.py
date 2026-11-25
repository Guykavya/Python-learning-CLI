import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB

from conftest import make_churn
from solution import calibrate

def ece_eq(y, p, bins=10):
    b = np.minimum(np.floor(p * bins).astype(int), bins - 1)
    tot = 0.0
    for k in range(bins):
        m = b == k
        if m.any():
            tot += abs(y[m].mean() - p[m].mean()) * m.sum()
    return tot / len(y)


class SpyNB(GaussianNB):
    fits = []

    def fit(self, X, y, sample_weight=None):
        SpyNB.fits.append(len(X))
        return super().fit(X, y, sample_weight=sample_weight)


def split(seed):
    d = make_churn(n=6000, seed=seed)
    X = pd.get_dummies(d.drop(columns="churned"), dtype=float).to_numpy()
    y = d["churned"].to_numpy()
    Xa, Xt, ya, yt = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    Xa, Xc, ya, yc = train_test_split(Xa, ya, test_size=0.3, random_state=seed, stratify=ya)
    return Xa, ya, Xc, yc, Xt, yt


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_calibration_improves_the_test_ece(seed):
    Xa, ya, Xc, yc, Xt, yt = split(seed)
    raw = GaussianNB().fit(Xa, ya).predict_proba(Xt)[:, 1]
    cal = calibrate(GaussianNB(), Xa, ya, Xc, yc).predict_proba(Xt)[:, 1]
    assert ece_eq(yt, raw) > 0.12, "sanity check: naive Bayes is badly calibrated here."
    assert ece_eq(yt, cal) < 0.08, f"after calibration the test ECE should be small, got {ece_eq(yt, cal):.3f}."
    assert abs(roc_auc_score(yt, cal) - roc_auc_score(yt, raw)) < 0.02, "sigmoid calibration keeps the ranking (AUC almost unchanged)."


def test_the_model_is_fitted_once_on_the_training_rows():
    Xa, ya, Xc, yc, Xt, yt = split(0)
    SpyNB.fits.clear()
    calibrate(SpyNB(), Xa, ya, Xc, yc)
    assert SpyNB.fits == [len(Xa)], f"fit the model once on the {len(Xa)} training rows; the calibrator must not refit it (use FrozenEstimator). Fits seen: {SpyNB.fits}."


def test_returns_a_fitted_probability_model():
    Xa, ya, Xc, yc, Xt, yt = split(1)
    cal = calibrate(GaussianNB(), Xa, ya, Xc, yc)
    p = cal.predict_proba(Xt)
    assert p.shape == (len(Xt), 2) and np.allclose(p.sum(axis=1), 1), "return the fitted calibrated classifier."
