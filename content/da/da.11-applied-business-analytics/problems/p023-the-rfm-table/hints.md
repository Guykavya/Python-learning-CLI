## Hint 1

First keep the orders on or before `asof`. Then one `groupby("customer_id")` with three aggregations. How do you turn the last order date into a number of days?

## Hint 2

```text
od = orders[orders.order_date <= asof]
g = od.groupby("customer_id").agg(last=("order_date","max"), F=("amount","size"), M=("amount","sum"))
g["R"] = (asof - g["last"]).dt.days
keep customers in the customers table; columns R, F, M
```
