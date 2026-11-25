## Approach

Each output column is a different question, so each gets the matching count, all inside one named aggregation
(Ch. 3.2): `size` counts rows whatever they hold, `count` skips missing values, `nunique` counts different values and
skips missing ones too.

## Code

```python
import pandas as pd


def customer_counts(lines):
    return lines.groupby("customer_id", as_index=False).agg(
        lines=("order_id", "size"),
        with_coupon=("coupon", "count"),
        distinct_products=("product_id", "nunique"),
    )
```

## Complexity

O(n) for the grouping and the counts (`nunique` hashes the values of each group), plus sorting the customers.

## Another way

Three separate grouped Series joined into one frame:

```python
g = lines.groupby("customer_id")
out = pd.DataFrame({"lines": g.size(), "with_coupon": g["coupon"].count(),
                    "distinct_products": g["product_id"].nunique()}).reset_index()
```
