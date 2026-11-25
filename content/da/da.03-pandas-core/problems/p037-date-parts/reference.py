import pandas as pd


def add_date_parts(df, col):
    d = df[col]
    out = df.copy()
    out["year"] = d.dt.year
    out["month"] = d.dt.month
    out["quarter"] = d.dt.quarter
    out["weekday"] = d.dt.day_name()
    out["is_weekend"] = d.dt.day_of_week >= 5
    return out
