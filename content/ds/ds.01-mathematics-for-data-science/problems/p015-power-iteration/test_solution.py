import math

import numpy as np
import pytest

from solution import power_iteration


def _sym(seed, n=5):
    rng = np.random.default_rng(seed)
    M = rng.normal(size=(n, n))
    return M @ M.T


def test_two_by_two_example():
    val, vec = power_iteration(np.array([[2.0, 1.0], [1.0, 2.0]]))
    assert val == pytest.approx(3.0, abs=1e-6), "the eigenvalues of [[2,1],[1,2]] are 3 and 1."
    assert abs(vec[0]) == pytest.approx(1 / math.sqrt(2), abs=1e-6), "the eigenvector is along [1, 1]."


def test_matches_eigh_on_random_symmetric_matrices():
    for seed in (1, 2, 3):
        A = _sym(seed)
        w, V = np.linalg.eigh(A)
        val, vec = power_iteration(A, steps=2000, seed=seed)
        assert val == pytest.approx(w[-1], rel=1e-6), "compare with the largest eigenvalue from np.linalg.eigh."
        assert abs(vec @ V[:, -1]) == pytest.approx(1.0, abs=1e-6), "the eigenvector matches up to sign."


def test_vector_has_unit_length_and_is_an_eigenvector():
    A = _sym(4)
    val, vec = power_iteration(A, steps=2000)
    assert np.linalg.norm(vec) == pytest.approx(1.0), "rescale to length 1 at every step."
    assert A @ vec == pytest.approx(val * vec, rel=1e-5, abs=1e-5), "A v must equal lambda v."


def test_same_seed_same_answer():
    A = _sym(5)
    a, b = power_iteration(A, steps=50, seed=7), power_iteration(A, steps=50, seed=7)
    assert a[0] == b[0] and np.array_equal(a[1], b[1]), "use np.random.default_rng(seed) for the start vector."


def test_large_number_of_steps_does_not_overflow():
    with np.errstate(over="raise", invalid="raise"):
        power_iteration(np.array([[10.0, 0.0], [0.0, 1.0]]), steps=5000)
