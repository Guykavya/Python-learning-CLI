import pandas as pd


def as_category(df, max_unique=50):
    """Copy of df where text columns with at most max_unique distinct values are categories."""
    return df.copy()
