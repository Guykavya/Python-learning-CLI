import pandas as pd


def p90(s):
    """90th percentile of one group's values."""
    return s.quantile(0.9)


def p90_delivery_days(orders):
    """One row per region: delivered, median_days, p90_days."""
    return orders.groupby("region", as_index=False).agg(
        delivered=("delivery_days", "count"),
        median_days=("delivery_days", "median"),
        p90_days=("delivery_days", p90),
    )
