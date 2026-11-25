import pandas as pd


def replace_sentinels(df, codes):
    """Replace code values by missing values; return (new_frame, count_per_column)."""
    raise NotImplementedError("for each column in codes: find the code values, count them, turn them into NaN")
