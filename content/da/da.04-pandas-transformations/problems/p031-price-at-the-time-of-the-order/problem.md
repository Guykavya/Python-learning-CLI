# The price at the time of the order

Chapter section 7.2. A price list says *from this day on, the price is X*. An order must use the **latest price that
was in force on or before its date**, for its own product. There is no exact key to match, so this is an as-of join.

Write `price_at_order(orders, price_history)`.

- `orders` has the columns `order_id`, `product_id`, `order_date`, `qty` (one row per order line).
- `price_history` has the columns `product_id`, `effective` (the first day of the price) and `price`.
- Both tables arrive **in any order**.

Return a new frame with all the columns of `orders` plus a column `price`, one row per order line (the row count must
not change), sorted by `order_id`, with a fresh index `0, 1, 2, ...`. A price that starts on the order day counts.
An order dated **before the first price** of its product gets a missing price (`NaN`). Do not change the inputs.

## Example

```python
import pandas as pd

orders = pd.DataFrame({
    "order_id": [2, 1, 3],
    "product_id": ["P1", "P1", "P2"],
    "order_date": pd.to_datetime(["2025-03-15", "2025-01-10", "2025-01-20"]),
    "qty": [1, 2, 1],
})
price_history = pd.DataFrame({
    "product_id": ["P1", "P2", "P1"],
    "effective": pd.to_datetime(["2025-03-01", "2025-02-01", "2025-01-01"]),
    "price": [120.0, 50.0, 100.0],
})
out = price_at_order(orders, price_history)
print(out["order_id"].tolist(), out["price"].tolist())
```
```text
[1, 2, 3] [100.0, 120.0, nan]
```

Order 3 is for `P2`, whose first price starts on 1 February, so it has no price yet. It must **not** borrow the price
of `P1`.
