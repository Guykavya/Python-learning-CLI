import pandas as pd


def summary_numbers(df):
    revenue = float((df["qty"] * df["unit_price"]).sum())
    units = int(df["qty"].sum())
    return {
        "orders": int(len(df)),
        "units": units,
        "revenue": revenue,
        "avg_price": revenue / units if units else None,
    }
