## Approach

The lambda does three things per group: mean, standard deviation, arithmetic. The first two exist as built-in
aggregations, and `transform` with their **names** runs them in compiled code for all groups at once, returning one
value per row aligned to the original index. The arithmetic is then one vectorised expression over whole columns. A
one-row group has a standard deviation of `NaN` (with `ddof=1`), and `x / NaN` is `NaN`, the same as the slow version.

## Code

```python
import pandas as pd


def zscore_by_group(df, key="store_id", col="revenue"):
    g = df.groupby(key)[col]
    return ((df[col] - g.transform("mean")) / g.transform("std")).rename("z")
```

## Complexity

O(n) for the two transforms plus O(n) arithmetic, with no Python call per group. The lambda version is O(n) too, but
with a large constant per group (a Python call and a small Series object each time), so its cost grows with the number
of groups.

## Another way

Aggregate once and merge back: `stats = df.groupby(key)[col].agg(["mean", "std"])`, then
`df[key].map(stats["mean"])` and `df[key].map(stats["std"])`. Same speed class, more lines. Always check the fast
version against the slow one on real data (`np.allclose`, with `equal_nan=True`) before you trust it.
