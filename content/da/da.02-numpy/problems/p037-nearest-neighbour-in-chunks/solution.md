## Approach

The full broadcast (Ch. 11.7) is the fastest code but needs memory proportional to n². Chunking (Ch. 17.4) keeps the vectorised inner step and adds an outer loop over **blocks of rows**: each block is compared with all points, its row minima are stored, and the block's temporaries are freed before the next one. The loop runs `n / chunk` times (48 times for 12,000 points), not n² times, so it stays fast.

Two details: the self-distance of row `r` of a block sits in column `start + r`, so the diagonal moves with the block; and the minimum of squared distances gives the same nearest point, so the square root is taken only once per point at the end.

## Code

```python
import numpy as np


def nearest_distance(points, chunk=250):
    points = np.asarray(points, dtype=float)
    n = len(points)
    if n < 2:
        raise ValueError(f"need at least 2 points, got {n}")
    if chunk < 1:
        raise ValueError(f"chunk must be at least 1, got {chunk}")
    best = np.empty(n)
    for start in range(0, n, chunk):
        block = points[start:start + chunk]
        d2 = ((block[:, None, :] - points[None, :, :]) ** 2).sum(axis=-1)
        rows = np.arange(len(block))
        d2[rows, start + rows] = np.inf
        best[start:start + len(block)] = d2.min(axis=1)
    return np.sqrt(best)
```

## Complexity

Time O(n² × d) as before: chunking does not reduce the work, only the memory, which drops from O(n² × d) to O(chunk × n × d). For 12,000 points in 2-D: about 3 seconds on the author's laptop (measured in an earlier test run), with a peak of a few tens of MB instead of more than 2 GB.

## Another way

For real nearest-neighbour search on many points, use a spatial index (a k-d tree, `scipy.spatial.cKDTree`, ds.06), which avoids comparing far-apart points at all: about O(n log n). The chunked broadcast is the general NumPy pattern for "my vectorised code ran out of memory", and it works for any per-pair computation.
