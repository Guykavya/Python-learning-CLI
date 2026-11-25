import polars as pl


def revenue_by_region_pl(items):
    """Polars: columns region, revenue (sum), orders (distinct order_id); revenue descending, ties by region."""
    return (items
            .group_by("region")
            .agg(pl.col("revenue").sum(), pl.col("order_id").n_unique().alias("orders"))
            .sort(["revenue", "region"], descending=[True, False]))
