import pandas as pd


def to_wide(monthly):
    """Long (store_id, month, sales) -> wide: store_id column, then one column per month."""
    keys = ["store_id", "month"]
    dup = monthly[monthly.duplicated(subset=keys, keep=False)]
    if len(dup):
        pairs = sorted(set(zip(dup["store_id"], dup["month"])))
        raise ValueError(f"(store_id, month) pairs repeat, e.g. {pairs[0]}: "
                         "pivot cannot add them up; use pivot_table with aggfunc='sum'")
    wide = monthly.pivot(index="store_id", columns="month", values="sales").reset_index()
    wide.columns.name = None
    return wide
