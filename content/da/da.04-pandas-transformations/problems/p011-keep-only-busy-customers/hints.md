## Hint 1

The rule "has at least 3 orders" is about the **customer**, not about one row. Which groupby method gives each
customer's sub-table to a function and keeps all its rows when the function says `True`? What is the number of
orders of a sub-table, when each row is one order?

## Hint 2

```text
orders.groupby("customer_id").filter(lambda d: len(d) >= min_orders)
# or, without a Python call per group:
orders[orders.groupby("customer_id")["order_id"].transform("size") >= min_orders]
```
