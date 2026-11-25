import numpy as np
import pandas as pd
import pytest

from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

from solution import kmeans_segments


def make(seed, n=200):
    rng = np.random.default_rng(seed)
    frames, truth = [], []
    for g, (r, f) in enumerate([(10, 12), (60, 4), (300, 1.5)]):
        R = np.exp(rng.normal(np.log(r), 0.25, n))
        F = np.exp(rng.normal(np.log(f), 0.25, n)).clip(min=1)
        M = F * np.exp(rng.normal(np.log(800), 0.25, n))
        frames.append(pd.DataFrame({"R": R, "F": F, "M": M}))
        truth += [g] * n
    return pd.concat(frames, ignore_index=True), np.array(truth)


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_recovers_three_groups(seed):
    d, truth = make(seed)
    labels, sil = kmeans_segments(d, 3, 0)
    assert adjusted_rand_score(truth, labels) > 0.9, "log1p and standardising must recover the three customer groups (adjusted Rand index above 0.9)."
    assert 0.3 < sil <= 1.0, f"well separated groups have a clearly positive silhouette, got {sil:.2f}"


def test_the_raw_version_would_fail_on_this_data():
    d, truth = make(0)
    raw = KMeans(3, n_init=10, random_state=0).fit(d[["R", "F", "M"]]).labels_
    assert adjusted_rand_score(truth, raw) < 0.6, "(data check) raw R, F, M cluster badly: the rupee column dominates; that is why you scale."


def test_types_and_reproducibility():
    d, _ = make(1, n=60)
    l1, s1 = kmeans_segments(d, 3, 7)
    l2, s2 = kmeans_segments(d, 3, 7)
    assert isinstance(l1, np.ndarray) and l1.dtype.kind == "i" and len(l1) == len(d), "labels: an int array, one per row."
    assert (l1 == l2).all() and s1 == s2 and type(s1) is float, "same seed, same result; the silhouette is a plain float."


def test_bad_k():
    d, _ = make(1, n=5)
    for k in (1, len(d)):
        with pytest.raises(ValueError, match="k must be between 2 and the number of customers minus 1"):
            kmeans_segments(d, k, 0)
