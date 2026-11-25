import numpy as np
import pytest
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score

from solution import elbow_and_silhouette


@pytest.fixture(scope="module")
def blobs():
    X, _ = make_blobs(n_samples=400, centers=[[0, 0], [8, 0], [0, 8], [8, 8]], cluster_std=0.8, random_state=1)
    return X


def test_silhouette_picks_the_true_number_of_clusters(blobs):
    table, best = elbow_and_silhouette(blobs, range(2, 8))
    assert best == 4, f"four well-separated blobs: the silhouette should peak at k = 4, got {best}."
    assert isinstance(best, int), "best_k is a plain int."


def test_table_shape_and_columns(blobs):
    table, _ = elbow_and_silhouette(blobs, [2, 3, 4])
    assert list(table.columns) == ["k", "inertia", "silhouette"], "columns: k, inertia, silhouette."
    assert table["k"].tolist() == [2, 3, 4], "one row per k, in the given order."


def test_inertia_falls_with_k_and_has_an_elbow(blobs):
    table, _ = elbow_and_silhouette(blobs, range(2, 8))
    inertia = table["inertia"].to_numpy()
    assert all(a > b for a, b in zip(inertia, inertia[1:])), "inertia falls as k grows."
    drops = -np.diff(inertia)
    assert drops[:2].min() > 5 * drops[2:].max(), "the big drops end at k = 4 (the elbow): later drops are tiny."


def test_values_match_a_direct_fit(blobs):
    table, _ = elbow_and_silhouette(blobs, [3], seed=2)
    km = KMeans(n_clusters=3, n_init=10, random_state=2).fit(blobs)
    assert table["inertia"].iloc[0] == pytest.approx(km.inertia_), "inertia is the model's inertia_."
    assert table["silhouette"].iloc[0] == pytest.approx(silhouette_score(blobs, km.labels_)), "silhouette_score(X, labels)."


def test_k_below_two_is_rejected(blobs):
    with pytest.raises(ValueError):
        elbow_and_silhouette(blobs, [1, 2, 3])
