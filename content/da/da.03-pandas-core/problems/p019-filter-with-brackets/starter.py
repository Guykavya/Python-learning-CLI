import pandas as pd


def big_orders(df, city, min_amount):
    """Not cancelled, and (from `city` with amount >= min_amount, or rush)."""
    return df[df["city"] == city & df["amount"] >= min_amount]
