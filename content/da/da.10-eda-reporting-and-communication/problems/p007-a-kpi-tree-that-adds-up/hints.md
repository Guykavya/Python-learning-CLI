## Hint 1

You need three counts per month: distinct customers, number of orders, sum of amounts. Which `agg` functions give each? The factors are ratios of these.

## Hint 2

```text
g = orders.groupby("month").agg(active=("customer_id", "nunique"), n_orders=("amount", "size"), revenue=("amount", "sum"))
orders_per_active = n_orders / active
avg_order_value = revenue / n_orders
```
