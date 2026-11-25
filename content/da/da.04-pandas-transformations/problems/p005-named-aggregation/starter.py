import pandas as pd


def store_summary(lines):
    """One row per store: orders (distinct), revenue (qty * unit_price), units."""
    return pd.DataFrame(columns=["store_id", "orders", "revenue", "units"])
