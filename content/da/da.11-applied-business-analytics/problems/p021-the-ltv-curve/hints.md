## Hint 1

For each order compute the bucket `(order_date - first_order).days // 30`. Which orders and which customers do you keep? How do you get from revenue per bucket to the cumulative revenue per customer?

## Hint 2

```text
eligible = customers with (asof - first_order).days >= 30*months + 29
o = orders of eligible customers, bucket b = days // 30, keep b <= months
per_bucket = o.groupby("b")["amount"].sum().reindex(range(months+1), fill_value=0)
curve = per_bucket.cumsum() / len(eligible)
```
