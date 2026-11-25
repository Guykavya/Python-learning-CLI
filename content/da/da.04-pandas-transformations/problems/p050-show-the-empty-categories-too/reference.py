import pandas as pd


def orders_per_size(df):
    """Columns size, orders: one row per category of df["size"], in order, 0 for unused sizes."""
    counts = df.groupby("size", observed=False).size()
    return counts.reset_index(name="orders")
