import math

import numpy as np
import pytest

from solution import cov_matrix


@pytest.fixture(autouse=True)
def _no_cov(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("this exercise is about doing it by hand: do not call np.cov.")
    monkeypatch.setattr(np, "cov", boom)


def test_worked_example():
    got = cov_matrix([[1, 2], [2, 4], [3, 6]])
    assert got == pytest.approx(np.array([[1, 2], [2, 4]])), "the second column is twice the first: [[1, 2], [2, 4]]."


def test_shape_symmetry_and_diagonal():
    rng = np.random.default_rng(5)
    X = rng.normal(size=(50, 4)) * [1, 2, 3, 4]
    C = cov_matrix(X)
    assert C.shape == (4, 4), f"expected a 4x4 matrix, got {C.shape}."
    assert C == pytest.approx(C.T), "a covariance matrix is symmetric."
    assert np.diag(C) == pytest.approx(X.var(axis=0, ddof=1)), "the diagonal holds the variances with n - 1 in the denominator."


def test_against_numpy_cov():
    rng = np.random.default_rng(6)
    X = rng.normal(size=(30, 3)) @ rng.normal(size=(3, 3)) + 10
    centred = X - X.mean(axis=0)
    expected = centred.T @ centred / 29
    assert cov_matrix(X) == pytest.approx(expected), "centre the columns, then Xc.T @ Xc / (n - 1)."


def test_shift_does_not_matter():
    rng = np.random.default_rng(7)
    X = rng.normal(size=(20, 3))
    assert cov_matrix(X + 100) == pytest.approx(cov_matrix(X)), "adding a constant to a column must not change the covariance: centre first."
