## Approach

Follow the written definition literally. The denominator is the customers present in the first week; the numerator is the ones among them whose last week is in the month. Customers who join and leave inside the month are in neither, as the definition says.

## Code

```python
import pandas as pd


def monthly_kpis(customers, panel):
    p = panel.assign(month=panel["week"].dt.to_period("M"))
    first = p.groupby("month")["week"].min()
    opening = p[p["week"].isin(first.values)][["customer_id", "month"]]
    opening = opening.merge(customers[["customer_id", "last_week"]], on="customer_id", how="left", validate="m:1")
    opening["churned"] = opening["last_week"].dt.to_period("M") == opening["month"]
    out = opening.groupby("month").agg(opening_actives=("customer_id", "size"), churned=("churned", "sum"))
    out["churn_rate_pct"] = out["churned"] / out["opening_actives"] * 100
    out["on_time_pct"] = (1 - p.groupby("month")["late"].mean()) * 100
    out["weekly_revenue_k"] = p.groupby(["month", "week"])["price"].sum().groupby("month").mean() / 1000
    return out
```

## Complexity

O(n log n) for the group-bys.

## Another way

`pd.crosstab` of month against `churned` gives the counts in one call; the explicit `agg` shows the definitions more clearly.
