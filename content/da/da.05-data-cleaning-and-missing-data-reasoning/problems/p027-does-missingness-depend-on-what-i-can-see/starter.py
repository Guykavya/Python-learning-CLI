def missingness_gap(df, col, other):
    """Mean of `other` where `col` is missing vs present, and the gap (missing minus present)."""
    raise NotImplementedError("split the rows by col.isna(), take the mean of other in each part")
