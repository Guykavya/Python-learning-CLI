import pandas as pd


def as_category(df, max_unique=50):
    """Copy of df where text columns with at most max_unique distinct values are categories."""
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_string_dtype(out[col]) and out[col].nunique() <= max_unique:
            out[col] = out[col].astype("category")
    return out
