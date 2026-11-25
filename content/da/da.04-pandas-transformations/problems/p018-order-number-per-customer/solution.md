## Approach

Sort a copy into time order; the original index labels travel with the rows. `cumcount() + 1` then numbers each
customer's orders 1, 2, 3, and the result is indexed by those original labels. Assigning it to the unsorted frame
**aligns by label**, so each order gets its own number while the rows stay where they were. The first orders are
simply the rows numbered 1.

## Code

```python
import pandas as pd


def number_orders(orders):
    ordered = orders.sort_values(["customer_id", "order_date", "order_id"])
    order_no = ordered.groupby("customer_id").cumcount() + 1
    return orders.assign(order_no=order_no)


def first_orders(orders):
    numbered = number_orders(orders)
    first = numbered[numbered["order_no"] == 1].drop(columns="order_no")
    return first.sort_values("customer_id", ignore_index=True)
```

## Complexity

O(n log n) for the sort; `cumcount` and the aligned assignment are O(n).

## Another way

For `first_orders` alone: sort, then `groupby("customer_id").head(1)`, or `drop_duplicates("customer_id")` on the
sorted frame (keeps the first row of each customer). `groupby(...).first()` is different: it takes the first
**non-missing value of each column** separately, which can mix values from different rows.
