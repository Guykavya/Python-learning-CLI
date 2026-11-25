## Approach

Sorting makes "first" and "second" positions in each group. Customers without a second row are exactly the one-order customers.

## Code

```python
import numpy as np
import pandas as pd


def days_to_second(orders):
    o = orders.sort_values(["customer_id", "order_date"])
    rank = o.groupby("customer_id").cumcount()
    first = o[rank == 0].set_index("customer_id")["order_date"]
    second = o[rank == 1].set_index("customer_id")["order_date"]
    days = (second - first.reindex(second.index)).dt.days.sort_index().astype(int)
    return {"days": days, "one_order": int(len(first) - len(second)),
            "median": float(days.median()) if len(days) else float("nan")}
```

## Complexity

O(n log n).

## Another way

`groupby("customer_id")["order_date"].apply(list)` and index into the lists: shorter, slower for large tables.
