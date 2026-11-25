## Approach

Every step is a `LazyFrame` method, so the function only builds a plan. The join with `validate="m:1"` makes Polars
check that each product appears once (a duplicated product would raise `ComputeError` at `collect()`). After the
per-product sums, one sort puts each category's best products first with ties in id order; `group_by(...,
maintain_order=True).head(n)` keeps the first `n` rows of each category and keeps the sorted order. `select` fixes the
column order.

## Code

```python
import polars as pl


def top_products_lazy(items, products, n=2):
    return (items
            .join(products, on="product_id", how="inner", validate="m:1")
            .with_columns((pl.col("qty") * pl.col("unit_price")).alias("revenue"))
            .group_by("category", "product_id").agg(pl.col("revenue").sum())
            .sort(["category", "revenue", "product_id"], descending=[False, True, False])
            .group_by("category", maintain_order=True).head(n)
            .select("category", "product_id", "revenue"))
```

## Complexity

O(n log n) for the sort; the join and group-by are hash-based. Being lazy, Polars reads only the columns it needs
(`list_price` is never touched), which you can see in `plan.explain()`.

## Another way

Rank inside the category with a window expression: add
`pl.col("revenue").rank("ordinal", descending=True).over("category")` after the sort by product id, and `filter` the
rank `<= n`. Or `.filter(pl.int_range(pl.len()).over("category") < n)` after the sort. All three give the same rows.
