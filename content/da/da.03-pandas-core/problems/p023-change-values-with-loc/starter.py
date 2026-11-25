import pandas as pd


def apply_discount(df, category, pct):
    """New frame with the price of every row in `category` reduced by pct percent."""
    df.loc[df["category"] == category, "price"] = df["price"] * (1 - pct / 100)
    return df
