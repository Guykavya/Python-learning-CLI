## Approach

With a two-level index, a tuple selects one (region, month) pair and a single label selects a whole region (a Series indexed by month). A pair that does not exist raises `KeyError`, which we turn into 0. The regions come from the first index level (`get_level_values`), sorted; for each one, `.loc[region, "sales"]` is the Series of its months, which we sum.

## Code

```python
import pandas as pd


def sales_for(df, region, month):
    multi = df.set_index(["region", "month"])
    try:
        return int(multi.loc[(region, month), "sales"])
    except KeyError:
        return 0


def sales_by_region(df):
    multi = df.set_index(["region", "month"])
    regions = sorted(multi.index.get_level_values("region").unique())
    return {r: int(multi.loc[r, "sales"].sum()) for r in regions}
```

## Complexity

`set_index` is O(n); each lookup is fast on a sorted or hashed index. The totals cost O(n) overall.

## Another way

`df.groupby("region")["sales"].sum()` is the usual way to get totals per region (da.04). `multi.xs("Jan", level="month")` selects one month across all regions.
