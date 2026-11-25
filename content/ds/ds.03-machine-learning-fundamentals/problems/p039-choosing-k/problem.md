# Choosing k

Chapter section 13. k-means needs `k` in advance. Two common guides:

- the **elbow**: the inertia always falls as `k` grows; look for the `k` after which it falls only slowly;
- the **silhouette score** (between -1 and 1): how well each point fits its own cluster compared with the nearest other cluster; higher is better; it is defined only for `k >= 2`.

Write `elbow_and_silhouette(X, ks, seed=0)` returning a tuple `(table, best_k)`:

- for every `k` in `ks` fit `KMeans(n_clusters=k, n_init=10, random_state=seed)` and record `inertia_` and `silhouette_score(X, labels)`
- `table`: a DataFrame with the columns `k, inertia, silhouette`, one row per `k`, in the order of `ks`
- `best_k`: the `k` with the highest silhouette (an `int`)
- any `k < 2` in `ks`: `ValueError`

## Example

```text
four well-separated blobs, ks = 2..7
 k  inertia  silhouette
 2   ...        0.62
 3   ...        0.64
 4   ...        0.76     <- best_k = 4
 5   ...        0.60
```
