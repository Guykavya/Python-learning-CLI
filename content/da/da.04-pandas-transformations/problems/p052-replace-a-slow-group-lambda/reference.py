import pandas as pd


def zscore_by_group(df, key="store_id", col="revenue"):
    """(value - group mean) / group std for every row, with built-in transforms only; a Series named "z"."""
    g = df.groupby(key)[col]
    return ((df[col] - g.transform("mean")) / g.transform("std")).rename("z")
