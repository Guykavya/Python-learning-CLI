## Approach

The anti-join is a yes/no test per customer, so a boolean mask is enough: `isin` checks each id against the order ids,
`~` keeps the ones **not** found. A mask can never duplicate rows or add columns, so the result is exactly the customer
rows, in their order. Orphan order keys (C9) are on the other side and cannot appear.

## Code

```python
import pandas as pd


def never_ordered(customers, orders):
    mask = ~customers["customer_id"].isin(orders["customer_id"])
    return customers[mask].reset_index(drop=True)
```

## Complexity

O(c + n): `isin` builds a hash set of the n order ids, then checks c customers.

## Another way

With a merge (Ch. 6.5): `customers.merge(orders[["customer_id"]].drop_duplicates(), on="customer_id", how="left",
indicator=True)`, keep `_merge == "left_only"`, then select the customer columns. The `drop_duplicates` matters: a
customer with 3 orders would otherwise be repeated 3 times before the filter.
