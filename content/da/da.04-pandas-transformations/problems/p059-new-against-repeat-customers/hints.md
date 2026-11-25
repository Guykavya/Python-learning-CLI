## Hint 1

For every order you need two months: the month of the order, and the month of the customer's **first** order. Which
groupby method puts "the earliest date of this customer" on every row, without collapsing the table? When are the two
months equal?

## Hint 2

```text
month = order_date as period "M"
first = orders.groupby("customer_id")["order_date"].transform("min") as period "M"
kind  = "new" where month == first, else "repeat"
per (month, kind): customer_id nunique and revenue sum -> unstack kind (fill 0)
make sure both "new" and "repeat" columns exist (reindex columns, fill 0)
build the five columns, month as text, sorted
```
