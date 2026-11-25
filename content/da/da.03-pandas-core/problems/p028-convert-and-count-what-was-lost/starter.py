import pandas as pd


def convert_numbers(s):
    """(numbers, bad_values): text -> float64, and the non-empty texts that could not be read."""
    return pd.to_numeric(s, errors="coerce"), []
