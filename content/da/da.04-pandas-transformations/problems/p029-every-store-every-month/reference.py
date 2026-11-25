import pandas as pd


def full_grid(sales, stores, months):
    """One row per store and month, revenue 0.0 where nothing was sold."""
    grid = stores[["store_id"]].merge(pd.DataFrame({"month": months}), how="cross")
    out = grid.merge(sales[["store_id", "month", "revenue"]], on=["store_id", "month"], how="left", validate="1:1")
    out["revenue"] = out["revenue"].fillna(0.0)
    return out.sort_values(["store_id", "month"], ignore_index=True)
