import math

import numpy as np
import pytest

from solution import matmul


def test_small_example():
    got = matmul([[1, 2], [3, 4]], [[0, 1], [1, 0]])
    assert np.array_equal(np.asarray(got), [[2, 1], [4, 3]]), "row-by-column: C[0][0] = 1*0 + 2*1 = 2."


def test_rectangular_shapes():
    A = np.arange(6.0).reshape(2, 3)
    B = np.arange(12.0).reshape(3, 4)
    got = np.asarray(matmul(A, B))
    assert got.shape == (2, 4), f"(2x3)(3x4) must give (2x4), got {got.shape}."
    assert got == pytest.approx(A @ B), "compare with A @ B entry by entry."


def test_order_matters():
    A, B = np.array([[1.0, 2.0], [3.0, 4.0]]), np.array([[0.0, 1.0], [1.0, 0.0]])
    assert not np.allclose(matmul(A, B), matmul(B, A)), "AB and BA are different matrices."


def test_not_elementwise():
    A = np.array([[1.0, 2.0], [3.0, 4.0]])
    assert not np.allclose(matmul(A, A), A * A), "matmul is the row-by-column product, not A * A."


def test_shape_mismatch_raises_and_names_shapes():
    with pytest.raises(ValueError) as e:
        matmul(np.ones((2, 3)), np.ones((2, 3)))
    assert "(2, 3)" in str(e.value), "put both shapes in the message, for example 'shapes (2, 3) and (2, 3) do not fit'."


def test_random_against_numpy():
    rng = np.random.default_rng(4)
    A, B = rng.normal(size=(4, 5)), rng.normal(size=(5, 3))
    assert np.asarray(matmul(A, B)) == pytest.approx(A @ B), "random 4x5 times 5x3."
