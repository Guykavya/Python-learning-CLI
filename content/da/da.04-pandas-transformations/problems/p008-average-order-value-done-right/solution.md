## Approach

A mean must know what it is the mean of. AOV is "per order", so the denominator is the number of **different** order
ids, both overall and per store. Never derive the overall figure from the store figures by a plain mean: it is right
only when every store has the same number of orders. The correct link is a **weighted** mean, weights = orders.

## Code

```python
import pandas as pd


def average_order_value(lines):
    rev = lines["qty"] * lines["unit_price"]
    overall = float(rev.sum() / lines["order_id"].nunique())
    by_store = (lines.assign(revenue=rev)
                     .groupby("store_id", as_index=False)
                     .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique")))
    by_store["aov"] = by_store["revenue"] / by_store["orders"]
    return overall, by_store
```

## Complexity

O(n) for the revenue column, the distinct count and the grouping.

## Another way

First aggregate to one row per order (`groupby("order_id").agg(store_id=("store_id", "first"), revenue=...)`), then
AOV is simply the mean of the order revenues, overall and per store. That makes the "per order" grain explicit and is
easy to check.
