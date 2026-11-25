import math

import numpy as np
import pytest

from solution import least_squares


@pytest.fixture(autouse=True)
def _no_lstsq(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("this exercise is about the normal equations: do not call np.linalg.lstsq.")
    monkeypatch.setattr(np.linalg, "lstsq", boom)


def test_exact_line():
    A = [[1, 0], [1, 1], [1, 2]]
    assert least_squares(A, [1, 3, 5]) == pytest.approx([1, 2]), "three points on y = 1 + 2x."


def test_recovers_known_coefficients_from_noisy_data():
    rng = np.random.default_rng(11)
    A = np.column_stack([np.ones(200), rng.normal(size=(200, 2))])
    true = np.array([2.0, -1.0, 0.5])
    b = A @ true + rng.normal(scale=0.01, size=200)
    assert least_squares(A, b) == pytest.approx(true, abs=0.01), "with tiny noise the coefficients must come back."


def test_matches_numpy_lstsq_and_residual_is_orthogonal():
    rng = np.random.default_rng(12)
    A, b = rng.normal(size=(30, 4)), rng.normal(size=30)
    x = least_squares(A, b)
    assert x == pytest.approx(np.linalg.pinv(A) @ b, rel=1e-6), "must agree with the library least-squares answer."
    assert A.T @ (b - A @ x) == pytest.approx(np.zeros(4), abs=1e-8), "the residual must be perpendicular to every column of A."


def test_square_system_is_just_solved():
    assert least_squares([[2, 0], [0, 4]], [2, 8]) == pytest.approx([1, 2]), "a square invertible system has an exact solution."
