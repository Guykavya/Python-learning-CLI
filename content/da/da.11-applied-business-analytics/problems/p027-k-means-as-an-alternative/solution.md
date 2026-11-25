## Approach

k-means measures **distances**, so every feature must have a comparable scale and a roughly symmetric distribution. After `log1p` and standardisation a unit difference means "about one standard deviation" in each of R, F and M.

## Code

```python
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
```

## Complexity

O(n x k x iterations).

## Another way

Run it for k = 3 ... 7 and compare the silhouette scores, but also check stability (do two random starts give the same groups? adjusted Rand index) and whether the clusters have a **business meaning**; a good score alone does not make a good segmentation.
