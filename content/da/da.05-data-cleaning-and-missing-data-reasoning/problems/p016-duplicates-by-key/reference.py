import pandas as pd


def dedupe_by_key(df, key, order_by):
    """Keep the row with the largest `order_by` for each `key`; return (kept, removed)."""
    work = df.reset_index(drop=True)
    winners = work.sort_values(order_by, kind="stable").drop_duplicates(subset=key, keep="last").index
    keep = work.index.isin(winners)
    return df[keep].copy(), df[~keep].copy()
