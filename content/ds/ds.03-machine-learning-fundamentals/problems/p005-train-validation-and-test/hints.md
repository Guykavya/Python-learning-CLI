## Hint 1

Shuffle the row numbers once, then cut that one list into three consecutive pieces. Why use the same shuffled list for `X` and `y`?

## Hint 2

```text
idx = default_rng(seed).permutation(n)
n_test = round(n * test); n_val = round(n * val)
test_idx = idx[:n_test]; val_idx = idx[n_test:n_test + n_val]; train_idx = idx[n_test + n_val:]
return X[train_idx], X[val_idx], X[test_idx], y[train_idx], y[val_idx], y[test_idx]
```
