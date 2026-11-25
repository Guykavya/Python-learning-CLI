## Approach

Give `a` an extra axis in the middle and `b` an extra axis in front: `(n, 1, d)` minus `(1, m, d)` broadcasts to `(n, m, d)`, every pair's coordinate differences. Square, sum over the last axis (the coordinates), take the square root: `(n, m)`. Subtracting the points directly makes identical points give exactly `0`.

## Code

```python
import numpy as np


def pairwise_distances(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape[1] != b.shape[1]:
        raise ValueError(f"points have {a.shape[1]} and {b.shape[1]} coordinates")
    diff = a[:, None, :] - b[None, :, :]
    return np.sqrt((diff ** 2).sum(axis=-1))
```

## Complexity

O(n × m × d) time and a temporary of n × m × d floats: for 2,000 × 2,000 × 3 that is 96 MB. For much larger sets, process `a` in chunks of rows (Ch. 17.4, problem p037).

## Another way

Expand the square: `|p - q|² = |p|² + |q|² - 2 p·q`, which turns the work into one matrix product:

```python
def pairwise_distances_dot(a, b):
    d2 = (a ** 2).sum(axis=1)[:, None] + (b ** 2).sum(axis=1)[None, :] - 2 * a @ b.T
    return np.sqrt(np.maximum(d2, 0.0))
```

It needs only an `(n, m)` temporary and is faster for large `d` (it is what libraries use for big data). But it subtracts large, nearly equal numbers and loses digits: for points around 1,000 the distance of a point to itself came out as large as `3e-5` instead of `0` in a test run (50 points), and 6 of the 50 squared self-distances were slightly negative, which would give `nan` without the `np.maximum`. That is why this problem's test of identical points rejects it: know the trick, and know its price.
