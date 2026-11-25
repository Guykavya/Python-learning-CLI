## Approach

`pivot` cannot add repeated (region, month) pairs; `pivot_table` can. `aggfunc="sum"` adds them, `fill_value=0` turns
empty pairs into 0 (here a missing pair really means "no sales"), and `margins=True` adds a total row and column
computed with the same `aggfunc`. Because the aggregation is a sum, the margins add up to the grand total; with
`"mean"` they would not (section 8.3).

## Code

```python
import pandas as pd


def region_month_table(items):
    return items.pivot_table(index="region", columns="month", values="revenue",
                             aggfunc="sum", fill_value=0, margins=True, margins_name="Total")
```

## Complexity

O(n) to group the lines plus O(regions × months) for the table.

## Another way

`items.groupby(["region", "month"])["revenue"].sum().unstack(fill_value=0)` gives the body; add the totals with
`t["Total"] = t.sum(axis=1)` and `t.loc["Total"] = t.sum()`. `pd.crosstab(items["region"], items["month"],
values=items["revenue"], aggfunc="sum", margins=True, margins_name="Total")` is another spelling (fill the gaps with
`fillna(0)`).
