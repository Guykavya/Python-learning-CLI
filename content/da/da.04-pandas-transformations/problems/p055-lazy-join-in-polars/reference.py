import polars as pl


def top_products_lazy(items, products, n=2):
    """A LazyFrame plan: top-n products by revenue per category (columns category, product_id, revenue)."""
    return (items
            .join(products, on="product_id", how="inner", validate="m:1")
            .with_columns((pl.col("qty") * pl.col("unit_price")).alias("revenue"))
            .group_by("category", "product_id").agg(pl.col("revenue").sum())
            .sort(["category", "revenue", "product_id"], descending=[False, True, False])
            .group_by("category", maintain_order=True).head(n)
            .select("category", "product_id", "revenue"))
