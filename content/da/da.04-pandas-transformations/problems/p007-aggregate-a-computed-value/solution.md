## Approach

Bring the category onto each line with a many-to-one merge (`validate="m:1"` makes pandas check that each product
appears once in `products`, so lines cannot be duplicated). Then compute the net revenue **on each line** with
`assign`, and only then sum per category. A product of sums is not a sum of products, so the order matters.

## Code

```python
import pandas as pd


def net_revenue_by_category(lines, products):
    net = lines.merge(products[["product_id", "category"]], on="product_id", how="left", validate="m:1")
    net = net.assign(net_revenue=net["qty"] * net["unit_price"] * (1 - net["discount"]))
    return net.groupby("category", as_index=False)["net_revenue"].sum()
```

## Complexity

O(n + p) for the hash merge (n lines, p products) and O(n) for the column and the grouping.

## Another way

Map instead of merge: `cat = lines["product_id"].map(products.set_index("product_id")["category"])`, then group the
computed Series by `cat`. `map` can never add rows, but it does not check for duplicated product ids either
(it raises a less clear error).
