## Hint 1

Which table holds the category, and which holds qty, price and discount? Before any grouping, what one column do you
need on every line? Why is "sum of quantities times sum of prices" not the same as "sum of quantity times price"?

## Hint 2

```text
x = lines.merge(products[["product_id", "category"]], on="product_id", how="left", validate="m:1")
x = x.assign(net_revenue = qty * unit_price * (1 - discount))      # per line
x.groupby("category", as_index=False)["net_revenue"].sum()
```
