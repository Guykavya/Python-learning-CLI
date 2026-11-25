## Approach

Sort first, so that the rows of each customer stand in date order (and the order id breaks same-day ties). Then
`groupby(...).cumsum()` adds up row by row and restarts at every customer, returning one value per row with the same
index, so it can be assigned straight back. `sort_values` returns a new frame, so the input is not touched.

## Code

```python
import pandas as pd


def running_spend(orders):
    out = orders.sort_values(["customer_id", "order_date", "order_id"], ignore_index=True)
    out["running_spend"] = out.groupby("customer_id")["amount"].cumsum()
    return out
```

## Complexity

O(n log n) for the sort, O(n) for the running sum.

## Another way

`transform("cumsum")` gives the same column. Without groupby, a loop over the sorted rows that resets the total when the
customer changes is what the test uses as its slow check.
