import pandas as pd


def yearly_long(df):
    """store_id + sales_<year>/units_<year> columns -> rows (store_id, year, sales, units)."""
    out = pd.wide_to_long(df, stubnames=["sales", "units"], i="store_id", j="year", sep="_").reset_index()
    out = out[["store_id", "year", "sales", "units"]]
    return out.sort_values(["store_id", "year"]).reset_index(drop=True)
