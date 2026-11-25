import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


def kmeans_segments(rfm, k, seed):
    """(labels as an int array, silhouette) of k-means on standardised log1p(R, F, M)."""
    raise NotImplementedError
