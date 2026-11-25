## Hint 1

In Polars the verb is `group_by`, and `agg` takes **expressions**, not tuples: `pl.col("revenue").sum()`. Which
expression counts distinct values, and how do you name its result `orders`? How does `sort` take two columns with
different directions?

## Hint 2

```text
items.group_by("region")
     .agg(pl.col("revenue").sum(), pl.col("order_id").n_unique().alias("orders"))
     .sort(["revenue", "region"], descending=[True, False])
```
