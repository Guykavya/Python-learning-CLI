import pandas as pd


def delivery_report(df):
    out = df.copy()
    out["days"] = (out["delivered"] - out["ordered"]) / pd.Timedelta(days=1)
    out["late"] = out["days"] > out["promised_days"]
    return out
