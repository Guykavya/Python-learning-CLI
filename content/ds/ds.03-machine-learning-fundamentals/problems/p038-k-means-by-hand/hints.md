## Hint 1

How do you get the squared distance from every point to every centre without a Python loop? Think of the shapes `(n, 1, d) - (1, k, d)`.

## Hint 2

```text
centres = init or X[rng.choice(...)]
repeat iters: d = ((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2); labels = d.argmin(axis=1)
    new = [X[labels == j].mean(axis=0) if any(labels == j) else centres[j] for j in range(k)]
    stop if allclose(new, centres); centres = new
final: recompute d, labels; inertia = d.min(axis=1).sum()
```
