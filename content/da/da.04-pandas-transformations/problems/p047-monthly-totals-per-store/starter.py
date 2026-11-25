import pandas as pd


def store_month(orders):
    """Columns store_id, month (month-end date), revenue: one row per store and month with orders."""
    # TODO: groupby(["store_id", pd.Grouper(key=..., freq=...)]), sum, back to columns
    raise NotImplementedError
