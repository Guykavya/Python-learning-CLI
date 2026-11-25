import math

import numpy as np
import pytest

from solution import loss_grad, fit_and_predict


def _data(seed=36, n=120):
    rng = np.random.default_rng(seed)
    X = np.column_stack([rng.normal(1.0, 0.5, n), rng.normal(1000.0, 300.0, n)])
    y = 5.0 + 3.0 * X[:, 0] + 0.01 * X[:, 1] + rng.normal(scale=0.1, size=n)
    return X, y


def test_the_gradient_passes_a_gradient_check():
    rng = np.random.default_rng(37)
    X, y, w = rng.normal(size=(30, 3)), rng.normal(size=30), rng.normal(size=3)
    loss = lambda v: float(np.mean((X @ v - y) ** 2))
    num = np.array([(loss(w + e) - loss(w - e)) / 2e-6 for e in np.eye(3) * 1e-6])
    got = loss_grad(w, X, y)
    err = np.linalg.norm(got - num) / (np.linalg.norm(got) + np.linalg.norm(num))
    assert err < 1e-6, f"loss_grad disagrees with the numerical gradient (relative error {err:.1e}): check the sign of the residual."


def test_predictions_are_finite():
    X, y = _data()
    with np.errstate(all="ignore"):
        pred = fit_and_predict(X, y, X[:5])
    assert np.all(np.isfinite(pred)), "the predictions are inf or nan: the descent diverges. Standardise the features and fix the gradient sign."


def test_predictions_match_least_squares():
    X, y = _data()
    X_new = np.array([[1.0, 800.0], [2.0, 1300.0], [0.5, 1000.0]])
    A = np.column_stack([np.ones(len(X)), X])
    ref = np.column_stack([np.ones(3), X_new]) @ np.linalg.lstsq(A, y, rcond=None)[0]
    with np.errstate(all="ignore"):
        got = fit_and_predict(X, y, X_new)
    assert got == pytest.approx(ref, abs=0.05), "after the fix the predictions must be close to the least-squares predictions."


def test_new_rows_use_the_training_statistics():
    X, y = _data()
    one = np.array([[1.5, 1100.0]])
    many = np.vstack([one, [[0.1, 300.0]], [[3.0, 2000.0]]])
    with np.errstate(all="ignore"):
        a = fit_and_predict(X, y, one)[0]
        b = fit_and_predict(X, y, many)[0]
    assert a == pytest.approx(b), "a row's prediction must not depend on the other new rows: scale X_new with the mean and std of X (training data)."
