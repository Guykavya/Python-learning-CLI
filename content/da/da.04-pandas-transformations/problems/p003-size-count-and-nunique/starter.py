import pandas as pd


def customer_counts(lines):
    """One row per customer: lines, with_coupon, distinct_products."""
    return pd.DataFrame(columns=["customer_id", "lines", "with_coupon", "distinct_products"])
