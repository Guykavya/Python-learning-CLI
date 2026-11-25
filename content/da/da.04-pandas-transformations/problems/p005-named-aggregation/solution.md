## Approach

Build the line revenue first (`assign` returns a new frame, so the input stays as it was), then one named aggregation
gives the three statistics with the exact names. "Orders" is a count of **different** order ids, so `nunique`.

## Code

```python
import pandas as pd


def store_summary(lines):
    return (lines.assign(revenue=lines["qty"] * lines["unit_price"])
                 .groupby("store_id", as_index=False)
                 .agg(orders=("order_id", "nunique"),
                      revenue=("revenue", "sum"),
                      units=("qty", "sum")))
```

## Complexity

O(n) for the product column and the grouping, plus sorting the stores.

## Another way

The older dictionary form `agg({"order_id": "nunique", "revenue": "sum", "qty": "sum"})` followed by
`rename(columns=...)` and `reset_index()` gives the same table, with more steps and names that can drift apart.
