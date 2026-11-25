# Running total per customer

Chapter section 5.1. A running total inside groups **restarts for every group**, and it follows the **row order**, so
sort first. Order matters: a running total over rows in the wrong order is a different (wrong) number.

Write `running_spend(orders)`. `orders` has columns `order_id`, `customer_id`, `order_date` (datetime) and `amount`,
in any order. Return a **new** frame:

- sorted by `customer_id`, then `order_date`, then `order_id` (two orders on the same day: the smaller id first);
- index `0, 1, 2, ...`;
- with an extra column `running_spend`: the customer's total spend up to and including that order.

Do not change `orders`.

## Example

```python
import pandas as pd

orders = pd.DataFrame({
    "order_id": [3, 1, 4, 2],
    "customer_id": ["A", "A", "B", "A"],
    "order_date": pd.to_datetime(["2025-01-05", "2025-01-02", "2025-01-01", "2025-01-05"]),
    "amount": [10.0, 20.0, 7.0, 5.0],
})
print(running_spend(orders))
```

```text
   order_id customer_id order_date  amount  running_spend
0         1           A 2025-01-02    20.0           20.0
1         2           A 2025-01-05     5.0           25.0
2         3           A 2025-01-05    10.0           35.0
3         4           B 2025-01-01     7.0            7.0
```
