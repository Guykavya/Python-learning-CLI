import pandas as pd


def average_order_value(lines):
    """Return (overall AOV as float, per-store frame store_id/revenue/orders/aov)."""
    return 0.0, pd.DataFrame(columns=["store_id", "revenue", "orders", "aov"])
