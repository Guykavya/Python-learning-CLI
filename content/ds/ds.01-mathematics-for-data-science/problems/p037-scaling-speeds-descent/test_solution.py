import math

import numpy as np
import pytest

from solution import steps_to_converge


def _stable_lr(X):
    lam = np.linalg.eigvalsh(2.0 / len(X) * X.T @ X).max()
    return 1.0 / lam


def _data(seed=38):
    rng = np.random.default_rng(seed)
    Z = rng.normal(size=(300, 2))
    Z = (Z - Z.mean(axis=0)) / Z.std(axis=0)
    y = Z @ [2.0, -1.0] + rng.normal(scale=0.1, size=300)
    return Z, y


def test_already_converged_start_returns_zero():
    X = np.eye(2)
    assert steps_to_converge(X, np.zeros(2), 0.1, 1e-6) == 0, "y = 0 means the gradient at w = 0 is already 0: zero steps."


def test_counts_steps_of_a_simple_problem():
    X, y = np.array([[1.0]]), np.array([1.0])
    n = steps_to_converge(X, y, 0.25, 1e-6)
    assert n == 21, f"w -> 0.5 w + 0.5, so the gradient is 2 * 0.5^k: it first drops below 1e-6 at step 21, got {n}."


def test_unscaled_features_need_far_more_steps():
    Z, y = _data()
    raw = Z * [1.0, 25.0]
    n_std = steps_to_converge(Z, y, _stable_lr(Z), 1e-6)
    n_raw = steps_to_converge(raw, y, _stable_lr(raw), 1e-6)
    assert n_raw > 10 * n_std, f"standardised data should need over 10 times fewer steps, got {n_std} (scaled) against {n_raw} (raw)."


def test_diverging_run_hits_the_cap():
    Z, y = _data(39)
    assert steps_to_converge(Z, y, 10.0, 1e-6, max_steps=200) == 200, "a learning rate that is far too big never converges: return max_steps."
