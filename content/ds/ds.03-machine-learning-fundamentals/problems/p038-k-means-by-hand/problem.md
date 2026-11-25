# k-means by hand

Chapter section 13. **k-means** groups points into `k` clusters. Start with `k` centres, then repeat two steps:

1. **assign** every point to its nearest centre (squared Euclidean distance);
2. **move** each centre to the mean of the points assigned to it (a centre with no points stays where it is).

Stop when the centres no longer change (`np.allclose`) or after `iters` rounds. The **inertia** is the sum of the squared distances from each point to its centre; it can only go down.

Write `kmeans(X, k, iters=100, seed=0, init=None)` returning `(centres, labels, inertia)`:

- `init` is an optional `(k, d)` array of starting centres; when it is `None` take `X[rng.choice(len(X), k, replace=False)]` with `rng = np.random.default_rng(seed)`
- after the loop assign every point once more to the final centres: `labels` (ints), and `inertia` (a float) belong to the **final centres**
- `k < 1` or `k > len(X)`: `ValueError`
- NumPy only; do not modify `X` or `init`

## Example

```text
three blobs around (0, 0), (6, 0), (3, 5), 600 points
centres, labels, inertia = kmeans(X, 3, init=one point from each blob)
-> three centres near the blob centres, inertia about 1137
```
