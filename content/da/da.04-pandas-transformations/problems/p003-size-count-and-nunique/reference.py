import pandas as pd


def customer_counts(lines):
    """One row per customer: lines, with_coupon, distinct_products."""
    return lines.groupby("customer_id", as_index=False).agg(
        lines=("order_id", "size"),
        with_coupon=("coupon", "count"),
        distinct_products=("product_id", "nunique"),
    )
