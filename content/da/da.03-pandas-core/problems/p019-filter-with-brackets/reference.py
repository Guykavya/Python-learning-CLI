import pandas as pd


def big_orders(df, city, min_amount):
    """Not cancelled, and (from `city` with amount >= min_amount, or rush)."""
    local_big = (df["city"] == city) & (df["amount"] >= min_amount)
    keep = (local_big | df["rush"]) & ~(df["status"] == "cancelled")
    return df[keep]
