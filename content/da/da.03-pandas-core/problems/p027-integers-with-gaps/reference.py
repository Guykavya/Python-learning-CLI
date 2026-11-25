import pandas as pd


def to_nullable_ints(df, cols):
    """Copy of df with the columns `cols` converted to Int64."""
    out = df.copy()
    for col in cols:
        try:
            out[col] = out[col].astype("Int64")
        except (TypeError, ValueError):
            raise ValueError("column %r has non-integer values" % col) from None
    return out
