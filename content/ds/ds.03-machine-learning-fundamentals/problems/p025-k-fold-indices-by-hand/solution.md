## Approach

One shuffle, then `np.array_split`, which already makes the folds as equal as possible (the first `n % k` folds get one extra element).

## Code

```python
import numpy as np


def kfold_indices(n, k, seed=0):
    if k < 2 or k > n:
        raise ValueError("need 2 <= k <= n")
    idx = np.random.default_rng(seed).permutation(n)
    return np.array_split(idx, k)
```

## Complexity

O(n).

## Another way

`sklearn.model_selection.KFold(k, shuffle=True, random_state=seed).split(...)` yields (train, test) pairs.
