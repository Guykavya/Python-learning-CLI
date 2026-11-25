## Approach

Eligibility fixes the **denominator** to customers whose 90-day window is complete. Among them, the second order is looked up per customer; a missing second order simply means "no repeat".

## Code

```python
import numpy as np
import pandas as pd


def repeat_rate_90d(orders, customers, asof):
    asof = pd.Timestamp(asof)
    elig = customers[customers["first_order"] <= asof - pd.Timedelta(days=90)]
    o = orders.sort_values(["customer_id", "order_date"])
    second = o.groupby("customer_id")["order_date"].nth(1)
    second.index = o.loc[second.index, "customer_id"].to_numpy()
    d = elig.set_index("customer_id")["first_order"]
    gap = (second.reindex(d.index) - d).dt.days
    repeaters = int((gap <= 90).sum())
    n = len(elig)
    return {"eligible": int(n), "repeaters": repeaters, "rate_pct": repeaters / n * 100 if n else float("nan")}
```

## Complexity

O(n log n).

## Another way

`groupby("customer_id")["order_date"].apply(lambda s: s.nsmallest(2).iloc[-1] if len(s) > 1 else NaT)` is easier to read and slower on large tables.
