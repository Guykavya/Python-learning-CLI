## Approach

`pd.Grouper(key="order_date", freq="ME")` is a grouping key that maps each date to its month-end bin. Combined with
`store_id` in one `groupby`, each (store, month) pair with orders becomes a group. Pairs without orders do not appear
when the Grouper is combined with another key (only observed combinations), which is what the task asks. `reset_index`
brings both keys back as columns.

## Code

```python
import pandas as pd


def store_month(orders):
    g = orders.groupby(["store_id", pd.Grouper(key="order_date", freq="ME")])["revenue"].sum()
    out = g.reset_index().rename(columns={"order_date": "month"})
    return out.sort_values(["store_id", "month"]).reset_index(drop=True)
```

## Complexity

O(n log n): the groupby sorts the keys.

## Another way

Make the month explicit first: `orders.assign(month=orders["order_date"] + pd.offsets.MonthEnd(0))` moves every date to
its month end (a date already at the end stays), then `groupby(["store_id", "month"])`. Or `dt.to_period("M")` if a
period label such as `2025-01` is enough.
