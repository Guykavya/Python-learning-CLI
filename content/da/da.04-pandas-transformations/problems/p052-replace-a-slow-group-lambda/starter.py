import pandas as pd


def zscore_by_group(df, key="store_id", col="revenue"):
    """(value - group mean) / group std for every row, with built-in transforms only; a Series named "z"."""
    # TODO: g = df.groupby(key)[col]; use g.transform("...") twice, then column arithmetic
    raise NotImplementedError
