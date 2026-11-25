import pandas as pd


def dedupe_by_key(df, key, order_by):
    """Keep the row with the largest `order_by` for each `key`; return (kept, removed)."""
    raise NotImplementedError("sort by order_by, keep the last row of each key, and also return what you removed")
