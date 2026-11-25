import pandas as pd


def missing_profile(df, by, col):
    t = df.assign(_missing=df[col].isna()).groupby(by)["_missing"].agg(["size", "sum"])
    t.columns = ["rows", "missing"]
    t["rate"] = t["missing"] / t["rows"]
    t = t.reset_index().sort_values(["rate", by], ascending=[False, True]).reset_index(drop=True)
    t["rows"] = t["rows"].astype(int)
    t["missing"] = t["missing"].astype(int)
    return t
