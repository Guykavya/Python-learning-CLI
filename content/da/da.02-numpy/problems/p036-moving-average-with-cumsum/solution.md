## Approach

Running totals turn every window sum into one subtraction: with `c[j] = x[0] + … + x[j-1]` (and `c[0] = 0`), the window `x[i : i + k]` sums to `c[i + k] - c[i]`. The slices `c[k:]` and `c[:-k]` line up all these pairs, so one vectorised subtraction gives every window (Ch. 12.1, example 3). The `0` in front is what makes the first window come out right.

## Code

```python
import numpy as np


def moving_average(x, k):
    x = np.asarray(x, dtype=float)
    if not 1 <= k <= x.size:
        raise ValueError(f"window k={k} must be between 1 and len(x)={x.size}")
    c = np.cumsum(np.insert(x, 0, 0.0))
    return (c[k:] - c[:-k]) / k
```

## Complexity

O(n) time and memory, whatever `k` is. Summing every window directly costs O(n × k): for `n = 10**6` and `k = 2 × 10**5` that is 1.6 × 10¹¹ additions.

## Another way

`np.convolve(x, np.ones(k) / k, mode="valid")` gives the same numbers in one call, and `sliding_window_view(x, k).mean(axis=1)` too; both are clear but cost O(n × k), fine for short windows. One caution for the cumsum trick: on very long series with large values, the running total grows large and the subtraction of two big, close numbers loses digits. Subtracting the mean first (`x - x.mean()`, then adding it back) keeps the totals small.
