import numpy as np
import pytest
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

from solution import kmeans


@pytest.fixture(scope="module")
def blobs():
    X, true = make_blobs(n_samples=600, centers=[[0, 0], [6, 0], [3, 5]], cluster_std=1.0, random_state=0)
    init = np.array([X[true == j][0] for j in range(3)])        # one starting point inside each blob
    return X, true, init


def test_finds_the_blobs(blobs):
    X, true, init = blobs
    centres, labels, inertia = kmeans(X, 3, init=init)
    expected = np.array([[0, 0], [6, 0], [3, 5]], dtype=float)
    for c in expected:
        assert np.min(np.linalg.norm(centres - c, axis=1)) < 0.3, f"no centre found near {c}."
    assert sorted(np.bincount(labels).tolist()) == [200, 200, 200], "each blob has 200 points and well-separated blobs must be recovered exactly."
    assert inertia == pytest.approx(1137.5, rel=0.02), "the inertia of the three blobs is about 1137."


def test_inertia_never_rises_with_more_iterations(blobs):
    X, _, _ = blobs
    vals = [kmeans(X, 3, iters=i, seed=5)[2] for i in range(1, 9)]
    for a, b in zip(vals, vals[1:]):
        assert b <= a + 1e-9, f"inertia rose from {a:.2f} to {b:.2f}: each assign/update round can only lower it."


def test_matches_sklearn_from_the_same_start(blobs):
    X, _, init = blobs
    _, _, inertia = kmeans(X, 3, init=init)
    sk = KMeans(3, init=init, n_init=1).fit(X)
    assert inertia == pytest.approx(sk.inertia_, rel=0.01), "within 1% of scikit-learn's inertia when both start from the same centres."


def test_labels_and_inertia_match_the_final_centres(blobs):
    X, _, init = blobs
    centres, labels, inertia = kmeans(X, 3, init=init)
    d = ((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2)
    assert np.array_equal(labels, d.argmin(axis=1)), "labels must be the nearest FINAL centre."
    assert inertia == pytest.approx(d.min(axis=1).sum()), "inertia is measured with the final centres."


def test_inputs_not_modified_and_seed_is_used(blobs):
    X, _, init = blobs
    X0, init0 = X.copy(), init.copy()
    kmeans(X, 3, init=init)
    assert np.array_equal(X, X0) and np.array_equal(init, init0), "do not modify X or init."
    a = kmeans(X, 3, seed=1)[0]
    b = kmeans(X, 3, seed=1)[0]
    assert np.allclose(a, b), "same seed, same initial centres, same result."


def test_empty_cluster_and_bad_k():
    X = np.array([[0.0, 0.0], [0.1, 0.0], [10.0, 10.0]])
    centres, labels, inertia = kmeans(X, 2, init=np.array([[0.0, 0.0], [50.0, 50.0]]))
    assert np.all(np.isfinite(centres)), "a centre that attracts no point stays where it is (no nan)."
    with pytest.raises(ValueError):
        kmeans(X, 4)
