import pandas as pd


def store_month(orders):
    """Columns store_id, month (month-end date), revenue: one row per store and month with orders."""
    g = orders.groupby(["store_id", pd.Grouper(key="order_date", freq="ME")])["revenue"].sum()
    out = g.reset_index().rename(columns={"order_date": "month"})
    return out.sort_values(["store_id", "month"]).reset_index(drop=True)
