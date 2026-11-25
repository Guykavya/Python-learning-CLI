import pandas as pd


def latest_per_customer(df):
    ordered = df.sort_values(["ts", "row_id"])
    latest = (ordered.drop_duplicates(subset="customer", keep="last")
                     .sort_values("customer").reset_index(drop=True))
    return latest, len(df) - len(latest)
