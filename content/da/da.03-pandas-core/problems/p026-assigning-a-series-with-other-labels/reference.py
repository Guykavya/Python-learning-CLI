import pandas as pd


def attach_targets(df, targets):
    """Copy of df with a `target` column looked up by customer_id; also the count of rows without a target."""
    out = df.copy()
    out["target"] = out["customer_id"].map(targets)
    n_missing = int((~out["customer_id"].isin(targets.index)).sum())
    return out, n_missing
