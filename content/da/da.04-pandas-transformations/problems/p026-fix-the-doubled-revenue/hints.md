## Hint 1

What is the grain (one row is ...) of `orders`, and what is the grain of `payments`? How many rows does the merge give
for order 1005, which had three attempts? Which number in the report is computed from those repeated rows?

## Hint 2

Bring `payments` to the grain of `orders` **before** merging, then the merge cannot repeat orders.

```text
pay = payments with is_paid = (status == "paid")
      grouped by order_id: n_payments = size, paid = any of is_paid
table = orders.merge(pay, on="order_id", how="left", validate="1:1")
n_payments: fillna(0) -> int;  paid: fillna(False) -> bool
check len(table) == len(orders), then compute the totals from table
```
