import pandas as pd


def to_long(wide):
    """Wide (store_id + one column per month) -> long (store_id, month, sales), sorted by store and month."""
    long = wide.melt(id_vars="store_id", var_name="month", value_name="sales")
    return long.sort_values(["store_id", "month"]).reset_index(drop=True)
