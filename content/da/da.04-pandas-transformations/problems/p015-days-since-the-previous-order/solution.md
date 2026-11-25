## Approach

Sort so that each customer's orders are in date order (order id breaks same-day ties). `groupby(...).diff()` subtracts
the previous row **of the same customer**, so the first order of every customer gets `NaT` instead of borrowing the
date of the customer above. `.dt.days` turns the `Timedelta` into whole days; `NaT` becomes `NaN`, so the column is
float. Two orders on the same day give a gap of 0 days, which is a real value, not a missing one.

## Code

```python
import pandas as pd


def days_between_orders(orders):
    out = orders.sort_values(["customer_id", "order_date", "order_id"], ignore_index=True)
    out["days_since_prev"] = out.groupby("customer_id")["order_date"].diff().dt.days
    return out
```

## Complexity

O(n log n) for the sort, O(n) for the differences.

## Another way

`shift` makes the "previous" value explicit: `prev = out.groupby("customer_id")["order_date"].shift(1)` and then
`(out["order_date"] - prev).dt.days`. Same result; useful when you also want to show the previous date.
