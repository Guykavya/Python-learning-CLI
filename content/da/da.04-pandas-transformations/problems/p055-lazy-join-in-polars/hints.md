## Hint 1

Write the pandas version in your head first: merge, new column, groupby-sum, sort, head per group. Every one of those
verbs exists on a `LazyFrame` (`join`, `with_columns`, `group_by().agg`, `sort`, `group_by().head`). Which column list
and `descending=` list give "category, then revenue high to low, then product id"?

## Hint 2

```text
(items.join(products, on="product_id", how="inner", validate="m:1")
      .with_columns((pl.col("qty") * pl.col("unit_price")).alias("revenue"))
      .group_by("category", "product_id").agg(pl.col("revenue").sum())
      .sort(["category", "revenue", "product_id"], descending=[False, True, False])
      .group_by("category", maintain_order=True).head(n)
      .select("category", "product_id", "revenue"))
```
