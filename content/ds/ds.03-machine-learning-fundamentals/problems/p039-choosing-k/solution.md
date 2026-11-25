## Approach

Fit one model per candidate `k`, tabulate the two numbers, and take the `k` with the best silhouette. The elbow in the inertia column is read by eye (it supports the same choice here).

## Code

```python
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
```

## Complexity

`len(ks)` k-means fits with 10 restarts each, plus an O(n^2) silhouette.

## Another way

The gap statistic compares the inertia with that of random data; it is more principled but more work.
