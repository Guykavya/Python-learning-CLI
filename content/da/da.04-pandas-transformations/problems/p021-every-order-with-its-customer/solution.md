## Approach

Orders are the main table, so they go on the left of a `left` join. `validate="m:1"` asks pandas to confirm that each
customer id appears at most once in `customers`; then the row count cannot change. `indicator=True` marks each row:
`left_only` means the order's customer was not found. Counting those gives the orphans, and dropping `_merge` leaves the
required columns.

## Code

```python
import pandas as pd


def orders_with_customers(orders, customers):
    table = orders.merge(customers, on="customer_id", how="left", validate="m:1", indicator=True)
    unknown = int((table["_merge"] == "left_only").sum())
    return table.drop(columns="_merge"), unknown
```

## Complexity

O(n + c) for a hash join of n orders and c customers.

## Another way

`unknown = int((~orders["customer_id"].isin(customers["customer_id"])).sum())` counts orphans without the merge.
Counting `table["city"].isna()` also works here, but it would also count a real customer whose city is missing in the
data; the indicator only counts missing **matches**.
