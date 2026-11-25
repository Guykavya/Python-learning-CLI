## Approach

The five numbers come from `np.percentile`. The whiskers are not the fences: they are the extreme data values that still lie inside the fences. Everything outside is an outlier.

## Code

```python
import numpy as np


def box_stats(x):
    x = np.sort(np.asarray(x, dtype=float))
    q1, med, q3 = np.percentile(x, [25, 50, 75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    inside = x[(x >= lo) & (x <= hi)]
    outliers = x[(x < lo) | (x > hi)]
    return {"q1": float(q1), "median": float(med), "q3": float(q3),
            "whisker_low": float(inside.min()), "whisker_high": float(inside.max()),
            "outliers": [float(v) for v in outliers]}
```

## Complexity

O(n log n) for the sort.

## Another way

`matplotlib.cbook.boxplot_stats(x)[0]` returns the same numbers (`q1`, `med`, `q3`, `whislo`, `whishi`, `fliers`); this is how `ax.boxplot` draws.
