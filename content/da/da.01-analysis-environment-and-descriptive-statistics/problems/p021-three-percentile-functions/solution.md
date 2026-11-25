## Approach

One sort, then a position, then (except nearest-rank) a linear interpolation `a + (b - a) * fraction`. Multiplying before dividing (`p * n / 100`) keeps integer arithmetic exact: `70 / 100 * 10` is `7.000000000000001` in floating point and `ceil` would then give 8 instead of 7.

## Code

```python
import math

def _prepare(values, p):
    if not values:
        raise ValueError("empty list")
    if not 0 <= p <= 100:
        raise ValueError("p must be between 0 and 100")
    return sorted(values)

def percentile_nearest_rank(values, p):
    s = _prepare(values, p)
    rank = max(1, math.ceil(p * len(s) / 100))
    return s[rank - 1]

def percentile_inclusive(values, p):
    s = _prepare(values, p)
    pos = (len(s) - 1) * p / 100
    lo = math.floor(pos)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)

def percentile_exclusive(values, p):
    s = _prepare(values, p)
    n = len(s)
    pos = (n + 1) * p / 100
    if pos < 1 or pos > n:
        raise ValueError(f"p={p} is too extreme for {n} values (exclusive)")
    lo = math.floor(pos)
    hi = min(lo + 1, n)
    return s[lo - 1] + (s[hi - 1] - s[lo - 1]) * (pos - lo)
```

## Complexity

O(n log n) per call because of the sort; O(n) space for the sorted copy.

## Another way

Sort once and compute many percentiles from the same sorted list (that is what `statistics.quantiles` does). For huge data, selection algorithms avoid the full sort.
