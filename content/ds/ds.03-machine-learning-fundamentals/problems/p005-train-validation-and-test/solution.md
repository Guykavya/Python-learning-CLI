## Approach

One permutation, three slices. Using the same index arrays for `X` and `y` keeps the pairs together, and the slices cannot overlap.

## Code

```python
import numpy as np


def three_way_split(X, y, val=0.2, test=0.2, seed=0):
    if val + test >= 1:
        raise ValueError("val + test must be below 1")
    X = np.asarray(X)
    y = np.asarray(y)
    n = len(X)
    idx = np.random.default_rng(seed).permutation(n)
    n_test = round(n * test)
    n_val = round(n * val)
    test_idx = idx[:n_test]
    val_idx = idx[n_test:n_test + n_val]
    train_idx = idx[n_test + n_val:]
    return X[train_idx], X[val_idx], X[test_idx], y[train_idx], y[val_idx], y[test_idx]
```

## Complexity

O(n) after the permutation.

## Another way

Call `train_test_split` twice (test first, then split the rest). The second call must use `val / (1 - test)` as its fraction, which is easy to get wrong.
