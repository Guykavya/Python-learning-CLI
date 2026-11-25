## Approach

The pandas version is `groupby("region").agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))`. In Polars,
the aggregations are expressions inside `agg`; an expression keeps the name of its column unless you `alias` it.
`n_unique` is Polars' `nunique`. Because the order of groups is not defined, sort explicitly, with a second key for
ties.

## Code

```python
import polars as pl


def revenue_by_region_pl(items):
    return (items
            .group_by("region")
            .agg(pl.col("revenue").sum(), pl.col("order_id").n_unique().alias("orders"))
            .sort(["revenue", "region"], descending=[True, False]))
```

## Complexity

O(n) for the hash grouping, plus sorting the regions.

## Another way

`items.lazy()` in front and `.collect()` at the end runs the same query as a lazy plan (section 13.6); for a small table
the result is identical. `pl.len()` would count *lines* instead of distinct orders.
