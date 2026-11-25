import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def elbow_and_silhouette(X, ks, seed=0):
    if any(k < 2 for k in ks):
        raise ValueError("every k must be at least 2 (the silhouette needs two clusters)")
    rows = []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(X)
        rows.append((k, float(km.inertia_), float(silhouette_score(X, km.labels_))))
    table = pd.DataFrame(rows, columns=["k", "inertia", "silhouette"])
    best_k = int(table.loc[table["silhouette"].idxmax(), "k"])
    return table, best_k
