import pandas as pd


def clean(df, log):
    out = df.copy()
    n_missing = int(out["price"].isna().sum())
    out["price"] = out["price"].fillna(out["price"].median())
    out["weight_kg"] = out["weight_g"] / 1000
    out = out[["item", "weight_kg", "price"]]
    log.append({"step": "clean", "rows": len(out), "price_filled": n_missing})
    return out
