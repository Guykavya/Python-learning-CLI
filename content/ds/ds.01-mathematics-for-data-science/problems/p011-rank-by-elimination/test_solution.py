import math

import numpy as np
import pytest

from solution import rank


@pytest.fixture(autouse=True)
def _no_library_rank(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("this exercise is about doing it by hand: do not call matrix_rank or svd.")
    monkeypatch.setattr(np.linalg, "matrix_rank", boom)
    monkeypatch.setattr(np.linalg, "svd", boom)


def test_small_cases():
    assert rank([[1, 2], [2, 4]]) == 1, "the second row is twice the first: rank 1."
    assert rank([[1, 0, 0], [0, 1, 0]]) == 2, "a wide matrix: two independent rows."
    assert rank([[0, 0], [0, 0]]) == 0, "the zero matrix has rank 0."
    assert rank(np.eye(4)) == 4, "the identity has full rank."


def test_non_square_shapes():
    assert rank(np.arange(12.0).reshape(4, 3)) == 2, "a 4x3 matrix of consecutive numbers has rank 2 (rows are arithmetic progressions)."
    assert rank(np.ones((5, 2))) == 1, "all-equal columns: rank 1."


def test_low_rank_products():
    rng = np.random.default_rng(9)
    for r in (1, 2, 3, 4):
        M = rng.normal(size=(7, r)) @ rng.normal(size=(r, 6))
        assert rank(M) == r, f"U (7x{r}) times V ({r}x6) has rank {r}: rounding noise must not add rank (use a tolerance)."


def test_a_zero_column_in_the_middle_does_not_stop_the_count():
    A = np.array([[1.0, 0.0, 2.0], [0.0, 0.0, 3.0], [0.0, 0.0, 0.0]])
    assert rank(A) == 2, "a column without a pivot must not advance the row counter."


def test_scaling_does_not_change_the_rank():
    rng = np.random.default_rng(10)
    M = rng.normal(size=(5, 2)) @ rng.normal(size=(2, 5))
    assert rank(M * 1e8) == 2 and rank(M * 1e-8) == 2, "the tolerance must be relative to the size of the matrix."
