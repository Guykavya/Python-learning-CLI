import math

import numpy as np
import pytest

from solution import compress


def _image(seed=24, n=64):
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 1, n)
    base = (np.outer(np.sin(3 * x), np.cos(2 * x)) * 5
            + np.outer(x, 1 - x) * 3
            + np.outer(np.exp(-4 * x), np.sin(7 * x)) * 1.5)
    return base + rng.normal(scale=0.02, size=(n, n))


def _rel_err(M, A):
    return np.linalg.norm(M - A) / np.linalg.norm(M)


def test_rank_one_matrix_needs_k_one():
    u, v = np.arange(1.0, 41.0), np.arange(1.0, 31.0)
    M = np.outer(u, v)
    approx, k, stored = compress(M, 0.05)
    assert k == 1, f"a rank-1 matrix is described exactly by k = 1, got {k}."
    assert stored == 1 * (40 + 30 + 1), "stored numbers = k * (m + n + 1) = 71."
    assert approx == pytest.approx(M, rel=1e-9), "the rank-1 approximation of a rank-1 matrix is the matrix."


def test_synthetic_image_k_is_smallest_and_error_below_tol():
    M = _image()
    approx, k, stored = compress(M, 0.05)
    s = np.linalg.svd(M, compute_uv=False)
    exact = lambda j: math.sqrt((s[j:] ** 2).sum()) / math.sqrt((s ** 2).sum())
    assert _rel_err(M, approx) < 0.05, f"the relative error must be below 5%, got {_rel_err(M, approx):.3f}."
    assert k == 1 or exact(k - 1) >= 0.05, f"k = {k} is not the smallest rank: rank {k - 1} already reaches the tolerance."
    assert k < 10, "three smooth patterns plus tiny noise should need only a handful of components."
    assert stored == k * (64 + 64 + 1), "stored = k * (m + n + 1)."


def test_a_stricter_tolerance_needs_more_components():
    M = _image(25)
    ks = [compress(M, t)[1] for t in (0.2, 0.05, 0.01)]
    assert ks == sorted(ks) and ks[0] < ks[-1], f"a smaller tolerance cannot need fewer components, got {ks}."


def test_rectangular_matrix_and_impossible_tolerance():
    rng = np.random.default_rng(26)
    M = rng.normal(size=(8, 5))
    approx, k, stored = compress(M, 1e-12)
    assert k == 5, "when only the full rank is accurate enough, return min(m, n)."
    assert approx.shape == (8, 5), "the approximation keeps the shape of M."
    assert stored == 5 * (8 + 5 + 1), "stored = k * (m + n + 1) even for a rectangular matrix."
