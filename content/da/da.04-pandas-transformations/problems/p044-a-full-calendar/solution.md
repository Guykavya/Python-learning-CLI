## Approach

`groupby` gives the days that exist. `reindex` with a complete `date_range` gives the days you *want*: labels that
were missing get `fill_value`, labels that are not in the new index (orders outside the period) are dropped. Choosing
0 is a business decision (the shop was open), which the task states.

## Code

```python
import pandas as pd


def daily_sales(orders, start, end):
    per_day = orders.groupby("order_date")["revenue"].sum()
    days = pd.date_range(start, end, freq="D")
    full = per_day.reindex(days, fill_value=0.0)
    return full.rename_axis("date").reset_index(name="revenue")
```

## Complexity

O(n) to group the orders plus O(d) for the d days of the calendar.

## Another way

`per_day.asfreq("D", fill_value=0.0)` fills the gaps *between* the first and last order day, but it cannot add days
before the first order or after the last one, and it does not cut off orders outside the period. `reindex` with an
explicit range does both.
