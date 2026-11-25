import math

import numpy as np
import pytest

from solution import pca


def _data(seed=13):
    rng = np.random.default_rng(seed)
    return rng.normal(size=(200, 4)) * [5.0, 2.0, 1.0, 0.2] @ np.linalg.qr(rng.normal(size=(4, 4)))[0]


def test_points_on_a_line():
    t = np.linspace(-3, 3, 20)
    comps, ratio = pca(np.column_stack([t, t]), 1)
    assert comps.shape == (1, 2), f"components must be k x d = (1, 2), got {comps.shape}."
    assert abs(comps[0, 0]) == pytest.approx(1 / math.sqrt(2)) and abs(comps[0, 1]) == pytest.approx(1 / math.sqrt(2)), "the line y = x has direction [1, 1]/sqrt(2)."
    assert ratio == pytest.approx([1.0]), "all the variance is along the line."


def test_matches_the_svd_up_to_sign():
    X = _data()
    comps, ratio = pca(X, 3)
    Xc = X - X.mean(axis=0)
    U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
    for i in range(3):
        assert abs(comps[i] @ Vt[i]) == pytest.approx(1.0, abs=1e-8), f"component {i} must match the SVD direction (up to sign); eigh is ascending, so reverse it."
    assert ratio == pytest.approx(s[:3] ** 2 / (s ** 2).sum()), "ratio = eigenvalue / sum of ALL eigenvalues."


def test_rows_are_unit_vectors_and_orthogonal():
    comps, ratio = pca(_data(), 4)
    assert comps @ comps.T == pytest.approx(np.eye(4), abs=1e-8), "components must be orthonormal."
    assert ratio.sum() == pytest.approx(1.0), "with k = d the ratios add up to 1."
    assert list(ratio) == sorted(ratio, reverse=True), "components must be sorted by explained variance, largest first."


def test_partial_ratio_is_below_one():
    comps, ratio = pca(_data(), 2)
    assert 0.5 < ratio.sum() < 1.0, "two of four components explain most, but not all, of the variance."


def test_shift_invariance():
    X = _data()
    a, ra = pca(X, 2)
    b, rb = pca(X + 50, 2)
    assert ra == pytest.approx(rb), "adding a constant must not change the explained variance (centre first)."
