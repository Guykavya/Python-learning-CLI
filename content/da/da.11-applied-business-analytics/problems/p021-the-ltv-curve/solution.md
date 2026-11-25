## Approach

The set of customers is fixed, so the curve can only go up; the first point is the average revenue of the first 30 days. Choosing the eligible set first, and only then computing revenue, avoids mixing mature and immature customers.

## Code

```python
import pandas as pd


def ltv_curve(orders, customers, asof, months):
    asof = pd.Timestamp(asof)
    cu = customers[(asof - customers["first_order"]).dt.days >= 30 * months + 29]
    if len(cu) == 0:
        raise ValueError("no customer has a full follow-up")
    o = orders.merge(cu[["customer_id", "first_order"]], on="customer_id", validate="m:1")
    o["b"] = (o["order_date"] - o["first_order"]).dt.days // 30
    per_bucket = o[o["b"] <= months].groupby("b")["amount"].sum().reindex(range(months + 1), fill_value=0.0)
    return (per_bucket.cumsum() / len(cu)).astype(float)
```

## Complexity

O(orders).

## Another way

Add the contribution margin and compare the curve with the acquisition cost: the month where it crosses CAC is the **payback period** (chapter section 4.5).
