import pandas as pd


def drop_exact_duplicates(df):
    """Remove rows that repeat an earlier row in every column; return (clean, number_removed)."""
    repeat = df.duplicated(keep="first")
    return df[~repeat].copy(), int(repeat.sum())
