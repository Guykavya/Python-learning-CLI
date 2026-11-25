import pandas as pd


def to_wide(long):
    """(store_id, month, sales) -> store_id + one column per sorted month; absent pairs are NaN."""
    wide = long.pivot(index="store_id", columns="month", values="sales").reset_index()
    wide.columns.name = None
    return wide


def to_long(wide):
    """Inverse of to_wide: drop missing cells, sales back to int64, sorted by store and month."""
    long = wide.melt(id_vars="store_id", var_name="month", value_name="sales")
    long = long.dropna(subset=["sales"]).astype({"sales": "int64"})
    return long.sort_values(["store_id", "month"]).reset_index(drop=True)
