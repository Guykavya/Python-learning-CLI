import pandas as pd


def split_full_name(df):
    parts = df["name"].str.split(n=1, expand=True).reindex(columns=[0, 1])
    out = df.copy()
    out["first"] = parts[0]
    out["last"] = parts[1].fillna("").where(df["name"].notna())
    return out
