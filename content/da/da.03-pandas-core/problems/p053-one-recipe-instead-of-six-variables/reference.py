import pandas as pd


def clean_orders(df):
    return (
        df
        .assign(city=lambda d: d["city"].str.strip().str.title())
        .query("qty > 0")
        .drop_duplicates(subset="order_id", keep="last")
        .assign(revenue=lambda d: d["qty"] * d["unit_price"] * (1 - d["discount"].fillna(0)))
        .query("paid")
        .sort_values("revenue", ascending=False)
        .reset_index(drop=True)
        .loc[:, ["order_id", "city", "revenue"]]
    )
