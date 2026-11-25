# Fix the doubled revenue

Chapter sections 6.3, 6.7 and 6.8. A colleague wrote a revenue report that attaches the payment status to each order.
Finance says the revenue in the report is far higher than the sum of the orders. The file `solution.py` already
contains this code; fix it.

```python
import pandas as pd


def revenue_report(orders, payments):
    """Revenue report: one row per order with its payment status."""
    table = orders.merge(payments, on="order_id", how="left")
    table["paid"] = table["status"] == "paid"
    table["n_payments"] = table.groupby("order_id")["payment_id"].transform("count")
    return {
        "total_revenue": float(table["amount"].sum()),
        "orders": len(table),
        "paid_orders": int(table["paid"].sum()),
        "table": table[["order_id", "customer_id", "amount", "n_payments", "paid"]],
    }
```

The tables:

- `orders`: one row per order: `order_id` (unique), `customer_id`, `amount`.
- `payments`: one row per **payment attempt**: `payment_id`, `order_id`, `status` (`"paid"`, `"failed"` or
  `"pending"`), `paid_amount`. An order can have **several** attempts (a failed card, then a paid one; or a bill split
  into two paid parts) or none at all. A payment can refer to an order that is not in `orders`; ignore it.

Required behaviour, a dictionary with:

- `"total_revenue"`: the sum of `amount` over the orders, each order **once** (a `float`);
- `"orders"`: the number of orders (an `int`);
- `"paid_orders"`: the number of orders with **at least one** payment whose status is `"paid"` (an `int`);
- `"table"`: one row per order, in the original order, index `0, 1, 2, ...`, columns `order_id`, `customer_id`,
  `amount`, `n_payments` (the number of attempts, an integer, `0` when there are none) and `paid` (`True`/`False`).

Do not change the inputs.

## Symptoms finance reported

1. "The total revenue is about double the order total."
2. "The report says we had more orders than the order system does."
3. "An order paid in two parts is counted as two paid orders."

## Example

```python
import pandas as pd

orders = pd.DataFrame({"order_id": [1, 2], "customer_id": ["C1", "C2"], "amount": [100.0, 50.0]})
payments = pd.DataFrame({"payment_id": ["X1", "X2"], "order_id": [1, 1],
                         "status": ["failed", "paid"], "paid_amount": [0.0, 100.0]})
report = revenue_report(orders, payments)
print(report["total_revenue"], report["orders"], report["paid_orders"])
print(report["table"])
```

```text
150.0 2 1
   order_id customer_id  amount  n_payments   paid
0         1          C1   100.0           2   True
1         2          C2    50.0           0  False
```
