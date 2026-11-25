## Hint 1

Which two scikit-learn objects give you the inertia and the labels of a fitted `KMeans`? Which function computes the silhouette from the data and the labels?

## Hint 2

```text
for k in ks: km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(X)
    rows.append((k, km.inertia_, silhouette_score(X, km.labels_)))
best_k = row with the largest silhouette
```
