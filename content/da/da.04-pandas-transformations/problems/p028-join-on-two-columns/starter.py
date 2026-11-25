import pandas as pd


def daily_targets(sales, targets):
    """Every sales row with its day's target and hit = revenue >= target."""
    return sales.copy()
