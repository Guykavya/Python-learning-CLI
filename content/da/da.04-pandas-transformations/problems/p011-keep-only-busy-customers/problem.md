# Keep only busy customers

Chapter section 4.2. `groupby(...).filter(func)` keeps or drops **whole groups**: `func` gets one group's sub-table
and returns `True` (keep all its rows) or `False`. It is not row filtering: the test is about the group, the result
is the original rows.

Write `busy_customers(orders, min_orders)`. `orders` has one row per order, with columns `order_id`, `customer_id` and
`store_id`, and any index. Return the rows of every customer who has **at least** `min_orders` orders: all of their
rows, in the original order, with the original index and columns. If nobody qualifies, return an empty frame with the
same columns. Do not change `orders`.

## Example

```python
import pandas as pd

orders = pd.DataFrame({"order_id": [1, 2, 3, 4, 5],
                       "customer_id": ["A", "B", "A", "C", "A"],
                       "store_id": ["S1", "S1", "S2", "S1", "S1"]})
print(busy_customers(orders, 2))
print(len(busy_customers(orders, 4)))
```

```text
   order_id customer_id store_id
0         1           A       S1
2         3           A       S2
4         5           A       S1
0
```
