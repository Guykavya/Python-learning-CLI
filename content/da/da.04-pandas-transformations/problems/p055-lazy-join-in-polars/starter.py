import polars as pl


def top_products_lazy(items, products, n=2):
    """A LazyFrame plan: top-n products by revenue per category (columns category, product_id, revenue)."""
    # TODO: join (inner, validate="m:1") -> revenue -> group_by + agg -> sort -> head per category -> select
    raise NotImplementedError
