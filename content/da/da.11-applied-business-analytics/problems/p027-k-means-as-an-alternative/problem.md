# k-means as an alternative

Chapter section 5.5. RFM scores need rules chosen by people. **k-means** lets the data propose groups. Two preparation steps matter: **recency, frequency and monetary value are very skewed** (a few customers spend 100 times the median),
and they are measured in different **units** (days, orders, rupees), so the one with the biggest numbers would decide everything.

Write `kmeans_segments(rfm, k, seed)`. `rfm` is a DataFrame with the columns `R`, `F`, `M` (non-negative). Do this, in this order:

1. `X = np.log1p(rfm[["R", "F", "M"]])`;
2. standardise each column (`sklearn.preprocessing.StandardScaler`);
3. `KMeans(n_clusters=k, n_init=10, random_state=seed)` fitted on the standardised data;
4. return `(labels, silhouette)`: `labels` as a NumPy int array in the row order of `rfm`, and the silhouette score of the standardised data and these labels (`sklearn.metrics.silhouette_score`) as a plain float.

If `k < 2` or `k >= len(rfm)`, raise `ValueError("k must be between 2 and the number of customers minus 1")`.

Cluster numbers are arbitrary labels (they can change between runs and versions): compare clusterings with the adjusted Rand index, never by label number.

## Example

On three clearly different customer groups with `k = 3` the clusters recover the groups (adjusted Rand index about 0.98 with the true groups); without the log and the scaling they do not (about 0.38).
