## Approach

The keep/drop decision belongs to each customer as a whole, so it is a group filter. `filter` hands each customer's
rows to the function and returns the original rows of the groups that pass, in the original order and with the
original index. An empty result keeps the columns.

## Code

```python
import pandas as pd


def busy_customers(orders, min_orders):
    return orders.groupby("customer_id").filter(lambda d: len(d) >= min_orders)
```

## Complexity

O(n) to group, plus one Python call per customer. Fine for thousands of customers; for millions use the
`transform` form below.

## Another way

A boolean mask built with `transform("size")` (Ch. 4.2): every row gets its customer's order count, and an ordinary
row filter does the rest. Same rows, no Python call per group:

```python
counts = orders.groupby("customer_id")["order_id"].transform("size")
busy = orders[counts >= min_orders]
```
