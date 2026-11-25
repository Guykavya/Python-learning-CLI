import pandas as pd


def daily_sales(orders, start, end):
    """One row per day from start to end (both included): columns date, revenue (0.0 on days without orders)."""
    per_day = orders.groupby("order_date")["revenue"].sum()
    days = pd.date_range(start, end, freq="D")
    full = per_day.reindex(days, fill_value=0.0)
    return full.rename_axis("date").reset_index(name="revenue")
