## Hint 1

Sort by customer and date, then take for each customer the first and the second date. Which pandas method picks the n-th row of each group? How do you count customers with a single order?

## Hint 2

```text
o = sort_values([customer_id, order_date]); g = o.groupby(customer_id)["order_date"]
first = g.nth(0), second = g.nth(1) (indexed by customer through the group key)
days = (second - first.reindex(second.index)).dt.days
one_order = number of customers - len(days)
```
