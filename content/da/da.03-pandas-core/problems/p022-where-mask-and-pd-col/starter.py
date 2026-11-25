import pandas as pd


def cap_discounts(df, cap):
    """Same table, but every discount above `cap` is set to `cap`."""
    return df[df["discount"] <= cap]
