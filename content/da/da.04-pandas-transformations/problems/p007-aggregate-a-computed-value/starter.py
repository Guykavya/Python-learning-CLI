import pandas as pd


def net_revenue_by_category(lines, products):
    """Net revenue (qty * unit_price * (1 - discount)) per category."""
    return pd.DataFrame(columns=["category", "net_revenue"])
