import pandas as pd


def convert_numbers(s):
    """(numbers, bad_values): text -> float64, and the non-empty texts that could not be read."""
    text = s.str.strip()
    numbers = pd.to_numeric(text, errors="coerce").astype("float64")
    lost = numbers.isna() & text.notna() & (text != "")
    bad_values = sorted(text[lost].unique().tolist())
    return numbers, bad_values
