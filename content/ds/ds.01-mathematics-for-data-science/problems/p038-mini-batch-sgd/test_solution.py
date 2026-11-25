import math

import numpy as np
import pytest

from solution import sgd


def _data(seed=40, n=200):
    rng = np.random.default_rng(seed)
    X = np.column_stack([np.ones(n), rng.normal(size=(n, 2))])
    y = X @ [1.0, 2.0, -1.0] + rng.normal(scale=0.5, size=n)
    return X, y


def _loss(w, X, y):
    return float(np.mean((X @ w - y) ** 2))


def test_same_seed_same_result_different_seed_differs():
    X, y = _data()
    a = sgd(X, y, 0.05, 5, 20, seed=1)
    b = sgd(X, y, 0.05, 5, 20, seed=1)
    c = sgd(X, y, 0.05, 5, 20, seed=2)
    assert np.array_equal(a, b), "the same seed must give exactly the same weights: create np.random.default_rng(seed) once."
    assert not np.array_equal(a, c), "another seed shuffles differently, so the weights should differ a little."


def test_ends_close_to_the_least_squares_loss():
    X, y = _data()
    best = _loss(np.linalg.lstsq(X, y, rcond=None)[0], X, y)
    w = sgd(X, y, 0.05, 40, 20, seed=0)
    assert _loss(w, X, y) < 1.05 * best, f"after 40 epochs the loss must be within 5% of the least-squares loss {best:.3f}, got {_loss(w, X, y):.3f}."


def test_full_batch_equals_plain_descent():
    X, y = _data(41)
    w = sgd(X, y, 0.1, 25, len(y), seed=0)
    ref = np.zeros(3)
    for _ in range(25):
        ref = ref - 0.1 * 2.0 / len(y) * (X.T @ (X @ ref - y))
    assert w == pytest.approx(ref), "with batch = n there is one batch per epoch: it is ordinary gradient descent (order of rows does not matter)."


def test_last_smaller_batch_uses_its_own_size():
    X, y = _data(42, n=45)
    w = sgd(X, y, 0.05, 1, 20, seed=3)
    order = np.random.default_rng(3).permutation(45)
    ref = np.zeros(3)
    for s in range(0, 45, 20):
        idx = order[s:s + 20]
        ref = ref - 0.05 * 2.0 / len(idx) * (X[idx].T @ (X[idx] @ ref - y[idx]))
    assert w == pytest.approx(ref), "one permutation per epoch from rng.permutation(n), chunks of `batch`, the last chunk divided by its own size."
