import pandas as pd


def apply_discount(df, category, pct):
    """New frame with the price of every row in `category` reduced by pct percent."""
    out = df.copy()
    rows = out["category"] == category
    out.loc[rows, "price"] = out.loc[rows, "price"] * (1 - pct / 100)
    return out
