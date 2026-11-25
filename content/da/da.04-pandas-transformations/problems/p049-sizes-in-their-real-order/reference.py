import pandas as pd

ORDER = ["S", "M", "L", "XL"]


def sort_by_size(df):
    """(out, n_unknown): size as an ordered categorical S < M < L < XL, rows sorted by it, invalid sizes counted."""
    known = df["size"].where(df["size"].isin(ORDER))
    n_unknown = int((df["size"].notna() & known.isna()).sum())
    dtype = pd.CategoricalDtype(ORDER, ordered=True)
    out = df.assign(size=known.astype(dtype)).sort_values("size", kind="stable").reset_index(drop=True)
    return out, n_unknown
