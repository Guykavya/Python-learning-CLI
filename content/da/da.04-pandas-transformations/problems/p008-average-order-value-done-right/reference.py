import pandas as pd


def average_order_value(lines):
    """Return (overall AOV as float, per-store frame store_id/revenue/orders/aov)."""
    rev = lines["qty"] * lines["unit_price"]
    overall = float(rev.sum() / lines["order_id"].nunique())
    by_store = (lines.assign(revenue=rev)
                     .groupby("store_id", as_index=False)
                     .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique")))
    by_store["aov"] = by_store["revenue"] / by_store["orders"]
    return overall, by_store
