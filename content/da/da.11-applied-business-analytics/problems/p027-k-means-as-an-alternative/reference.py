import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


def kmeans_segments(rfm, k, seed):
    if k < 2 or k >= len(rfm):
        raise ValueError("k must be between 2 and the number of customers minus 1")
    X = StandardScaler().fit_transform(np.log1p(rfm[["R", "F", "M"]]))
    km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(X)
    return km.labels_.astype(int), float(silhouette_score(X, km.labels_))
