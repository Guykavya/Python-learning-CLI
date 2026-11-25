import math

import numpy as np
import pytest

from solution import mse_grad


def _loss(w, X, y):
    return float(np.mean((X @ w - y) ** 2))


def _num(w, X, y, h=1e-6):
    g = np.zeros_like(w)
    for i in range(len(w)):
        e = np.zeros_like(w); e[i] = h
        g[i] = (_loss(w + e, X, y) - _loss(w - e, X, y)) / (2 * h)
    return g


def test_worked_value():
    assert mse_grad(np.array([0.0]), np.array([[1.0], [2.0]]), np.array([1.0, 2.0])) == pytest.approx([-5.0]), "2/n * X.T @ (Xw - y) = -5 here."


def test_gradient_check_on_random_data():
    rng = np.random.default_rng(28)
    for _ in range(5):
        X, y, w = rng.normal(size=(40, 4)), rng.normal(size=40), rng.normal(size=4)
        got = mse_grad(w, X, y)
        assert got.shape == (4,), f"the gradient has one entry per weight, got shape {got.shape}."
        assert got == pytest.approx(_num(w, X, y), rel=1e-5, abs=1e-6), "compare with a numerical gradient: check the factor 2/n and the sign."


def test_zero_at_the_least_squares_solution():
    rng = np.random.default_rng(29)
    X, y = rng.normal(size=(60, 3)), rng.normal(size=60)
    w = np.linalg.lstsq(X, y, rcond=None)[0]
    assert mse_grad(w, X, y) == pytest.approx(np.zeros(3), abs=1e-9), "the gradient vanishes at the best-fit weights."


def test_points_uphill():
    rng = np.random.default_rng(30)
    X, y, w = rng.normal(size=(30, 2)), rng.normal(size=30), np.zeros(2)
    step = w - 1e-3 * mse_grad(w, X, y)
    assert _loss(step, X, y) < _loss(w, X, y), "moving AGAINST the gradient must lower the loss (check the sign)."
