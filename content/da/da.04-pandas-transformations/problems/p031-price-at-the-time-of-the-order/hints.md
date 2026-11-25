## Hint 1

`pd.merge_asof` matches each left row to the last right row whose time is at or before its own. Which argument keeps
the matching inside one product, and what does pandas require about the order of both tables?

## Hint 2

```text
left  = orders sorted by order_date
right = price_history sorted by effective
out = merge_asof(left, right, left_on="order_date", right_on="effective",
                 by="product_id", direction="backward")
drop the effective column, sort by order_id, reset the index
```
