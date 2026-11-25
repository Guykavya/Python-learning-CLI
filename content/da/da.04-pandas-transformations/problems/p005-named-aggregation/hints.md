## Hint 1

`revenue` is not a column yet, and `agg` can only aggregate columns that exist. How can you add it without changing
the caller's frame? For "orders", is the right count `size`, `count` or `nunique` of `order_id`?

## Hint 2

```text
lines.assign(revenue = qty * unit_price)          # a new frame, input untouched
     .groupby("store_id", as_index=False)
     .agg(orders=("order_id", "nunique"), revenue=("revenue", "sum"), units=("qty", "sum"))
```
