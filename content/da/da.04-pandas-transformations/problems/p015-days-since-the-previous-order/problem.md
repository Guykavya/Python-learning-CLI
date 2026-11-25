# Days since the previous order

Chapter section 5.1. `groupby(...).diff()` subtracts the **previous row of the same group**; the first row of each
group has no previous row and gets a missing value. On dates the difference is a `Timedelta`; `.dt.days` turns it into
a number of days.

Write `days_between_orders(orders)`. `orders` has columns `order_id`, `customer_id` and `order_date` (datetime), in
any order. Return a **new** frame:

- sorted by `customer_id`, then `order_date`, then `order_id`; index `0, 1, 2, ...`;
- with an extra column `days_since_prev`: whole days since the same customer's previous order (a float column);
  **missing** for each customer's first order; `0.0` for a second order on the same day.

Do not change `orders`.

## Example

```python
import pandas as pd

orders = pd.DataFrame({
    "order_id": [1, 2, 3, 4],
    "customer_id": ["A", "B", "A", "A"],
    "order_date": pd.to_datetime(["2025-01-01", "2025-01-03", "2025-01-11", "2025-01-11"]),
})
print(days_between_orders(orders))
```

```text
   order_id customer_id order_date  days_since_prev
0         1           A 2025-01-01              NaN
1         3           A 2025-01-11             10.0
2         4           A 2025-01-11              0.0
3         2           B 2025-01-03              NaN
```
