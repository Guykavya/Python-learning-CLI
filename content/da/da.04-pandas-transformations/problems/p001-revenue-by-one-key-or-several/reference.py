import pandas as pd


def revenue_by(lines, keys):
    """Total revenue per key (a column name or a list of names), keys as columns, sorted."""
    if isinstance(keys, str):
        keys = [keys]
    return lines.groupby(keys, as_index=False)["revenue"].sum()
