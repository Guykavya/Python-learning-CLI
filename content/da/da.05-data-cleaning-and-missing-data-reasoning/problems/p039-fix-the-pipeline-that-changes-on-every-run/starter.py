import pandas as pd

LOG = []


def clean(df, log):
    """Grams to kilograms, fill missing prices with the median price, write one log line."""
    df["weight_g"] = df["weight_g"] / 1000
    n_missing = int(df["price"].isna().sum())
    df["price"] = df["price"].fillna(df["price"].median())
    out = df.rename(columns={"weight_g": "weight_kg"})
    LOG.append({"step": "clean", "rows": len(out), "price_filled": n_missing})
    return out[["item", "weight_kg", "price"]]
