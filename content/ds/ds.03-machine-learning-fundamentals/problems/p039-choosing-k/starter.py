import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def elbow_and_silhouette(X, ks, seed=0):
    """(DataFrame k, inertia, silhouette; best_k by silhouette)."""
    raise NotImplementedError
