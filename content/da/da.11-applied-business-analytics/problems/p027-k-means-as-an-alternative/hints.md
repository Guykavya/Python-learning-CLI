## Hint 1

Which transformation tames a long right tail and keeps zeros defined? Which step makes days, orders and rupees comparable? Does the silhouette score belong to the raw or the scaled data?

## Hint 2

```text
X = StandardScaler().fit_transform(np.log1p(rfm[["R","F","M"]]))
km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(X)
return km.labels_, float(silhouette_score(X, km.labels_))
```
