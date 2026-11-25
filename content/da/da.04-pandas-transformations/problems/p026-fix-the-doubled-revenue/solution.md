## Approach

The bug is **fan-out** (Ch. 6.8). `orders` has one row per order; `payments` has one row per attempt. Merging them
repeats every order once per attempt, so `amount` is summed two or three times (symptom 1), `len(table)` counts
attempts (symptom 2), and a bill paid in two parts gives two `True` rows (symptom 3). Nothing crashes; only the numbers
are wrong.

The fix is to **aggregate the many side to the grain of the base table first**: one row per order with the number of
attempts and "any attempt paid". Then the merge is one-to-one; `validate="1:1"` makes pandas guarantee it and a
row-count check documents it. Orders without attempts get `0` and `False` instead of missing values. A payment for an
unknown order disappears in the left join, as required.

## Code

```python
import pandas as pd


def revenue_report(orders, payments):
    pay = (payments.assign(is_paid=payments["status"] == "paid")
                   .groupby("order_id", as_index=False)
                   .agg(n_payments=("payment_id", "size"), paid=("is_paid", "any")))
    table = orders.merge(pay, on="order_id", how="left", validate="1:1")
    assert len(table) == len(orders), "the merge changed the number of orders"
    table["n_payments"] = table["n_payments"].fillna(0).astype(int)
    table["paid"] = table["paid"].fillna(False).astype(bool)
    return {
        "total_revenue": float(table["amount"].sum()),
        "orders": len(table),
        "paid_orders": int(table["paid"].sum()),
        "table": table[["order_id", "customer_id", "amount", "n_payments", "paid"]],
    }
```

## Complexity

O(n + p): one grouping pass over p payments, one hash join with n orders.

## Another way

Avoid the merge entirely with `map`: `counts = payments.groupby("order_id").size()` and
`paid_ids = payments.loc[payments["status"] == "paid", "order_id"]`, then
`n_payments = orders["order_id"].map(counts).fillna(0).astype(int)` and `paid = orders["order_id"].isin(paid_ids)`.
`map` and `isin` can never add rows, so fan-out is impossible.
