## Approach

Count first, divide second. Because `n_orders` appears once in a numerator and once in a denominator, the product of the factors equals `revenue` exactly (up to floating point).

## Code

```python
import pandas as pd


def revenue_tree(orders):
    g = orders.groupby("month").agg(active=("customer_id", "nunique"), n_orders=("amount", "size"),
                                    revenue=("amount", "sum")).sort_index()
    g["orders_per_active"] = g["n_orders"] / g["active"]
    g["avg_order_value"] = g["revenue"] / g["n_orders"]
    return g[["active", "orders_per_active", "avg_order_value", "revenue"]]
```

## Complexity

O(n log n).

## Another way

Compute the month-on-month change of each factor in logs: `log(revenue)` is the sum of the logs of the factors, so the changes add up exactly. That is how a revenue change is split into "more customers", "more orders each" and "bigger baskets".
