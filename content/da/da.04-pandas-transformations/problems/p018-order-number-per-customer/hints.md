## Hint 1

`cumcount` numbers rows in the order they stand, so you must sort first. But the result must come back in the
**original** order. What does pandas do when you assign a Series whose index labels are in a different order from the
frame's?

## Hint 2

```text
ordered  = orders.sort_values(["customer_id", "order_date", "order_id"])   # labels travel with the rows
order_no = ordered.groupby("customer_id").cumcount() + 1                    # indexed by the original labels
out      = orders.assign(order_no=order_no)                                 # aligned by label
first_orders: rows of number_orders(...) with order_no == 1, drop order_no, sort by customer_id, reset index
```
