import math

import numpy as np
import pytest

from solution import pinv


@pytest.fixture(autouse=True)
def _no_library_pinv(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("this exercise is about doing it by hand: do not call np.linalg.pinv.")
    monkeypatch.setattr(np.linalg, "pinv", boom)


def test_diagonal_with_a_zero():
    got = pinv(np.diag([2.0, 0.5, 0.0]))
    assert got == pytest.approx(np.diag([0.5, 2.0, 0.0])), "invert 2 and 0.5, but leave the zero singular value at 0."


def test_shape_and_penrose_equation():
    rng = np.random.default_rng(22)
    A = rng.normal(size=(6, 3))
    P_ = pinv(A)
    assert P_.shape == (3, 6), f"an m x n matrix has an n x m pseudo-inverse, got {P_.shape}."
    assert A @ P_ @ A == pytest.approx(A, abs=1e-9), "A A+ A must give back A."
    assert P_ @ A == pytest.approx(np.eye(3), abs=1e-9), "for a tall full-rank matrix A+ A = I."


def test_rank_deficient_matrix():
    rng = np.random.default_rng(23)
    A = rng.normal(size=(5, 2)) @ rng.normal(size=(2, 4))
    ref = np.linalg.svd(A, full_matrices=False)
    s = ref[1]; keep = s > 1e-10 * s.max()
    expected = (ref[2].T[:, keep] / s[keep]) @ ref[0].T[keep]
    assert pinv(A) == pytest.approx(expected, abs=1e-8), "rank 2: invert only the two non-zero singular values."


def test_underdetermined_gives_the_shortest_solution():
    A = np.array([[1.0, 1.0, 0.0], [0.0, 1.0, 1.0]])
    b = np.array([2.0, 2.0])
    x = pinv(A) @ b
    assert A @ x == pytest.approx(b), "x must solve the system."
    other = x + np.array([1.0, -1.0, 1.0])
    assert A @ other == pytest.approx(b), "(sanity check of the test: this vector also solves it)."
    assert np.linalg.norm(x) < np.linalg.norm(other), "pinv(A) @ b must be the solution of minimum length."


def test_scaled_matrix_and_zero_matrix():
    A = np.diag([1.0, 1e-4]) * 1e8
    assert pinv(A) == pytest.approx(np.diag([1e-8, 1e-4]), rel=1e-8), "the cutoff must be relative: 1e4 is not tiny next to 1e8."
    assert pinv(np.zeros((2, 3))) == pytest.approx(np.zeros((3, 2))), "the pseudo-inverse of the zero matrix is the zero matrix."
