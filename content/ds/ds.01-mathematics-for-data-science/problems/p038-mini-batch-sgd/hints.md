## Hint 1

How many batches does one epoch have if `n = 205` and `batch = 20`? How do you slice `order[i:i + batch]` for the last, shorter one?

## Hint 2

```text
rng = default_rng(seed); w = zeros(d)
for epoch in range(epochs):
    order = rng.permutation(n)
    for start in range(0, n, batch):
        idx = order[start:start + batch]
        w -= lr * 2/len(idx) * X[idx].T @ (X[idx] @ w - y[idx])
```
