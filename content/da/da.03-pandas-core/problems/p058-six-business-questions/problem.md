# Six business questions

Chapter sections 16 and 19.6. On a **cleaned** orders table (one row per order) answer six questions with six
functions. The columns are `order_date` (datetime), `customer`, `product`, `channel` (text), `qty`, `unit_price` and
`returned` (bool: the order was sent back). **Returned orders do not count as sales**, except in the last question.
The revenue of an order is `qty * unit_price`. (Without `groupby`, which comes in da.04, use `resample`,
`value_counts` and masks.)

| function | returns |
|---|---|
| `revenue_by_month(df)` | a Series indexed by month text `"2025-01"`, **every** month from the first to the last order (all rows), value = revenue of non-returned orders in that month (`0.0` when none) |
| `top_products(df, n=5)` | a list of `(product, orders)` pairs for the `n` products with the most non-returned orders, most first; equal counts ordered by product name A to Z |
| `channel_share(df)` | a dict `channel -> share of non-returned orders` (the shares add up to 1) |
| `average_order_value(df)` | revenue of non-returned orders divided by their number (a `float`) |
| `repeat_customer_share(df)` | among customers with at least one non-returned order, the share that has **two or more** (a `float`) |
| `returns_rate(df)` | the share of **all** orders that were returned (a `float`) |

The input frame is not changed. Python scalars and lists, not numpy types, where the table says `float` or list.

## Example

```python
import pandas as pd

from solution import revenue_by_month, top_products, returns_rate

df = pd.DataFrame({
    "order_date": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-03-02", "2025-03-09", "2025-03-09"]),
    "customer": ["A", "B", "A", "C", "A"],
    "product": ["tea", "tea", "rice", "tea", "rice"],
    "channel": ["web", "shop", "web", "web", "shop"],
    "qty": [2, 1, 3, 1, 2],
    "unit_price": [100.0, 100.0, 50.0, 100.0, 50.0],
    "returned": [False, False, False, True, False],
})
print(revenue_by_month(df).to_dict())
print(top_products(df, n=2))
print(returns_rate(df))
```

```text
{'2025-01': 300.0, '2025-02': 0.0, '2025-03': 250.0}
[('rice', 2), ('tea', 2)]
0.2
```
