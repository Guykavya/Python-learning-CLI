import math

import numpy as np
import pytest

from solution import fit_linear_gd


def _data(seed=32, n=200):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 3))
    X = (X - X.mean(axis=0)) / X.std(axis=0)
    y = 2.0 + X @ [1.0, -2.0, 0.5] + rng.normal(scale=0.3, size=n)
    return X, y


def test_exact_line():
    w = fit_linear_gd(np.array([[-1.0], [0.0], [1.0]]), np.array([1.0, 3.0, 5.0]), 0.1, 500)
    assert w == pytest.approx([3.0, 2.0], abs=1e-4), "y = 3 + 2x: the intercept comes first, then the slope."


def test_matches_lstsq():
    X, y = _data()
    A = np.column_stack([np.ones(len(X)), X])
    ref = np.linalg.lstsq(A, y, rcond=None)[0]
    got = fit_linear_gd(X, y, 0.1, 1000)
    assert got.shape == (4,), f"[intercept, w1, w2, w3] expected, got shape {got.shape}."
    assert got == pytest.approx(ref, abs=1e-3), "after enough steps descent must reach the least-squares solution (intercept column first)."


def test_more_steps_get_closer():
    X, y = _data(33)
    A = np.column_stack([np.ones(len(X)), X])
    ref = np.linalg.lstsq(A, y, rcond=None)[0]
    e1 = np.linalg.norm(fit_linear_gd(X, y, 0.05, 10) - ref)
    e2 = np.linalg.norm(fit_linear_gd(X, y, 0.05, 100) - ref)
    assert e2 < e1, "a hundred steps must be closer to the solution than ten."


def test_zero_steps_returns_zeros():
    X, y = _data(34)
    assert fit_linear_gd(X, y, 0.1, 0) == pytest.approx(np.zeros(4)), "start from zero weights."


def test_does_not_change_inputs():
    X, y = _data(35)
    X0, y0 = X.copy(), y.copy()
    fit_linear_gd(X, y, 0.1, 5)
    assert np.array_equal(X, X0) and np.array_equal(y, y0), "build the design matrix as a new array."
