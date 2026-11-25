import pandas as pd


def store_summary(lines):
    """One row per store: orders (distinct), revenue (qty * unit_price), units."""
    return (lines.assign(revenue=lines["qty"] * lines["unit_price"])
                 .groupby("store_id", as_index=False)
                 .agg(orders=("order_id", "nunique"),
                      revenue=("revenue", "sum"),
                      units=("qty", "sum")))
