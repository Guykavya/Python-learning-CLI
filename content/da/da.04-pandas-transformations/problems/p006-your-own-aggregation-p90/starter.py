import pandas as pd


def p90(s):
    """90th percentile of one group's values."""
    raise NotImplementedError


def p90_delivery_days(orders):
    """One row per region: delivered, median_days, p90_days."""
    return pd.DataFrame(columns=["region", "delivered", "median_days", "p90_days"])
