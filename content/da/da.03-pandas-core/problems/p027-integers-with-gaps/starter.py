import pandas as pd


def to_nullable_ints(df, cols):
    """Copy of df with the columns `cols` converted to Int64."""
    return df.astype({c: "int64" for c in cols})
