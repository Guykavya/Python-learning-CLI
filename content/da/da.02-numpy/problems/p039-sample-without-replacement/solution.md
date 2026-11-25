## Approach

Sample positions, then index. `rng.choice(n, size=k, replace=False)` draws `k` distinct integers from `0 … n-1`; `x[idx]` is fancy indexing (Ch. 9), which returns a **copy** with those rows in the drawn order, so `x` is never touched and the result is independent of it. Working with positions also handles equal rows correctly: they are different positions.

## Code

```python
import numpy as np


def sample_rows(x, k, rng):
    x = np.asarray(x)
    n = len(x)
    if not 0 <= k <= n:
        raise ValueError(f"cannot pick k={k} different rows from n={n}")
    idx = rng.choice(n, size=k, replace=False)
    return x[idx]
```

## Complexity

O(n) time and memory for the positions in the worst case, plus O(k × m) for the copied rows.

## Another way

`rng.permutation(n)[:k]` shuffles all positions and keeps the first `k`: also correct, but it always does O(n) work. `rng.choice(x, size=k, replace=False, axis=0)` samples rows directly from the array. What you must not do is `rng.shuffle(x)` (in place, it reorders the caller's data) and then take `x[:k]`.
