import math

import numpy as np
import pytest

from solution import logloss_grad


def _loss(w, X, y):
    z = X @ w
    return float(np.mean(np.logaddexp(0, z) - y * z))


def _num(w, X, y, h=1e-6):
    g = np.zeros_like(w)
    for i in range(len(w)):
        e = np.zeros_like(w); e[i] = h
        g[i] = (_loss(w + e, X, y) - _loss(w - e, X, y)) / (2 * h)
    return g


def test_worked_value():
    got = logloss_grad(np.array([0.0]), np.array([[1.0], [-1.0]]), np.array([1.0, 0.0]))
    assert got == pytest.approx([-0.5]), "X.T @ (sigmoid(z) - y) / n = -0.5 here."


def test_gradient_check():
    rng = np.random.default_rng(31)
    for _ in range(5):
        X, w = rng.normal(size=(50, 3)), rng.normal(size=3)
        y = (rng.random(50) < 0.5).astype(float)
        assert logloss_grad(w, X, y) == pytest.approx(_num(w, X, y), rel=1e-5, abs=1e-7), "compare with a numerical gradient: X.T @ (sigmoid(Xw) - y) / n."


def test_no_overflow_for_huge_scores():
    X = np.array([[1.0], [-1.0], [1.0], [-1.0]])
    w = np.array([800.0])
    y = np.array([1.0, 0.0, 0.0, 1.0])
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        g = logloss_grad(w, X, y)
    assert np.all(np.isfinite(g)), "the gradient must be finite even when z = +-800."
    assert g == pytest.approx([0.5]), "rows 3 and 4 are confidently wrong: X.T @ (p - y) / n = (1 + 1) / 4 = 0.5."


def test_confident_correct_predictions_have_zero_gradient():
    X = np.array([[1.0], [-1.0]])
    with np.errstate(over="raise"):
        g = logloss_grad(np.array([1000.0]), X, np.array([1.0, 0.0]))
    assert g == pytest.approx([0.0], abs=1e-12), "both points are classified right with certainty: nothing to correct."


def test_confident_wrong_predictions_have_a_bounded_gradient():
    X = np.array([[1.0]])
    with np.errstate(over="raise"):
        g = logloss_grad(np.array([-1000.0]), X, np.array([1.0]))
    assert g == pytest.approx([-1.0]), "sigmoid(-1000) = 0, so the gradient is X.T @ (0 - 1) = -1: bounded, not infinite."
