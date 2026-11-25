# Order number per customer

Chapter section 5.4. `cumcount()` numbers the rows inside each group from 0, in the order the rows stand. Add 1 and
you have "this is the customer's 1st, 2nd, 3rd order", the column analysts use to separate **new** from **repeat**
purchases.

Write two functions. `orders` has columns `order_id`, `customer_id` and `order_date` (datetime), in any order and with
any index.

- `number_orders(orders)` returns a **new** frame with the same rows **in the same order and with the same index** as
  the input, plus a column `order_no`: 1 for the customer's earliest order, 2 for the next, and so on. Orders are put in
  time order by `order_date`, and two orders on the same day by `order_id` (smaller first).
- `first_orders(orders)` returns each customer's first order (the one with `order_no` 1): the input's columns only,
  one row per customer, sorted by `customer_id`, index `0, 1, 2, ...`.

Do not change `orders`.

## Example

```python
import pandas as pd

orders = pd.DataFrame({
    "order_id": [5, 1, 3],
    "customer_id": ["B", "A", "A"],
    "order_date": pd.to_datetime(["2025-02-01", "2025-01-10", "2025-01-05"]),
}, index=[10, 11, 12])
print(number_orders(orders))
print(first_orders(orders))
```

```text
    order_id customer_id order_date  order_no
10         5           B 2025-02-01         1
11         1           A 2025-01-10         2
12         3           A 2025-01-05         1
   order_id customer_id order_date
0         3           A 2025-01-05
1         5           B 2025-02-01
```
