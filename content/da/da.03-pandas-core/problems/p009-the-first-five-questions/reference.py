import pandas as pd


def first_look(df):
    """rows, cols, dtypes (as text), missing per column, duplicate_rows."""
    return {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "missing": {c: int(n) for c, n in df.isna().sum().items()},
        "duplicate_rows": int(df.duplicated().sum()),
    }
