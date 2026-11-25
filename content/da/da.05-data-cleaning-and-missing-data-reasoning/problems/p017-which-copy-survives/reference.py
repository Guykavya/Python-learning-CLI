import pandas as pd


def best_copy(df, key):
    """One row per key: the most complete copy; ties go to the latest updated_at, then to the later row."""
    work = df.reset_index(drop=True)
    work["_filled"] = work.notna().sum(axis=1)
    order = work.sort_values(["_filled", "updated_at"], kind="stable")
    winners = order.drop_duplicates(subset=key, keep="last").index
    return df[work.index.isin(winners)].copy()
