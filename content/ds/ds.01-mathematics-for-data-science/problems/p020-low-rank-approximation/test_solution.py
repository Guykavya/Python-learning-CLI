import math

import numpy as np
import pytest

from solution import low_rank


def test_diagonal_example():
    got = low_rank(np.diag([3.0, 2.0, 1.0]), 2)
    assert got == pytest.approx(np.diag([3.0, 2.0, 0.0]), abs=1e-9), "drop the smallest singular value."


def test_shape_and_rank():
    rng = np.random.default_rng(19)
    M = rng.normal(size=(8, 5))
    got = low_rank(M, 2)
    assert got.shape == M.shape, f"the approximation must have the shape of M, got {got.shape}."
    assert np.linalg.matrix_rank(got) == 2, "the result must have rank exactly k."


def test_eckart_young_error():
    rng = np.random.default_rng(20)
    M = rng.normal(size=(10, 6))
    s = np.linalg.svd(M, compute_uv=False)
    for k in (1, 2, 4):
        err = np.linalg.norm(M - low_rank(M, k))
        assert err == pytest.approx(math.sqrt((s[k:] ** 2).sum())), f"the error for k = {k} must be sqrt(sum of the dropped s^2): keep the LARGEST singular values."


def test_full_rank_gives_back_the_matrix_and_zero_gives_zeros():
    rng = np.random.default_rng(21)
    M = rng.normal(size=(5, 4))
    assert low_rank(M, 4) == pytest.approx(M), "keeping all singular values reproduces M."
    assert low_rank(M, 0) == pytest.approx(np.zeros_like(M)), "k = 0 gives the zero matrix."


def test_a_rank_one_matrix_is_recovered_with_k_one():
    u, v = np.array([1.0, 2.0, 3.0]), np.array([4.0, 5.0])
    M = np.outer(u, v)
    assert low_rank(M, 1) == pytest.approx(M), "an outer product has rank 1: k = 1 loses nothing."
