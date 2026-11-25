## Approach

The as-of filter comes first, so that everything below is about the past only. The inner join with `customers` keeps only known customers.

## Code

```python
import pandas as pd


def rfm_table(orders, customers, asof):
    asof = pd.Timestamp(asof)
    od = orders[orders["order_date"] <= asof]
    g = od.groupby("customer_id").agg(last=("order_date", "max"), F=("amount", "size"), M=("amount", "sum"))
    g["R"] = (asof - g["last"]).dt.days.astype(int)
    g = g[g.index.isin(customers["customer_id"])]
    return g[["R", "F", "M"]].sort_index()
```

## Complexity

O(n log n).

## Another way

Build the table for two as-of dates (a past one and today) to test whether the segments predict the future (chapter section 5.4).
