## Approach

Aggregate first (one bar per category), then sort ascending, because the last bar of `barh` ends up at the top. The baseline is fixed at 0 so the lengths compare honestly.

## Code

```python
import matplotlib.pyplot as plt


def category_bars(df, cat, val):
    totals = df.groupby(cat)[val].sum().sort_values()
    fig, ax = plt.subplots()
    ax.barh([str(c) for c in totals.index], totals.values)
    ax.set_xlim(left=0)
    ax.set_xlabel(val)
    return fig
```

## Complexity

O(n log n) for the sort.

## Another way

Sort descending and call `ax.invert_yaxis()`: the first bar is then at the top. Both give the same picture; this test accepts either.
