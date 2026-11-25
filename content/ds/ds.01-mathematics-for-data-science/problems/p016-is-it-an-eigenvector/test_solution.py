import math

import numpy as np
import pytest

from solution import is_eigenvector

A = np.array([[2.0, 0.0], [0.0, 3.0]])


def test_axis_vectors_are_eigenvectors():
    ok, lam = is_eigenvector(A, [1, 0])
    assert ok is True and lam == pytest.approx(2.0), "[1, 0] is scaled by 2."
    ok, lam = is_eigenvector(A, [0, 5])
    assert ok is True and lam == pytest.approx(3.0), "any multiple of an eigenvector is an eigenvector."


def test_a_mixed_vector_is_not():
    assert is_eigenvector(A, [1, 1]) == (False, None), "A [1, 1] = [2, 3] is not a multiple of [1, 1]."


def test_zero_vector_is_never_an_eigenvector():
    assert is_eigenvector(A, [0, 0]) == (False, None), "A 0 = lam 0 for every lam: by definition v must be non-zero."


def test_symmetric_example_from_numpy():
    M = np.array([[2.0, 1.0], [1.0, 2.0]])
    w, V = np.linalg.eigh(M)
    for k in range(2):
        ok, lam = is_eigenvector(M, V[:, k])
        assert ok is True and lam == pytest.approx(w[k]), f"eigenpair {k} from eigh must be accepted."
    assert is_eigenvector(M, [1, 0]) == (False, None), "[1, 0] is not an eigenvector of [[2,1],[1,2]]."


def test_non_symmetric_matrix_and_tolerance():
    M = np.array([[1.0, 1.0], [0.0, 2.0]])
    ok, lam = is_eigenvector(M, [1, 0])
    assert ok is True and lam == pytest.approx(1.0), "[1, 0] has eigenvalue 1 for this upper-triangular matrix."
    ok, lam = is_eigenvector(M, [1, 1 + 1e-12])
    assert ok is False or lam == pytest.approx(2.0, abs=1e-6), "a tiny rounding difference must not change the answer wildly."
