import re

import pandas as pd

NA_TEXT = {"", "n/a", "-999"}


def _parse_one(value):
    if value is None or pd.isna(value):
        return float("nan")
    text = str(value).strip().lower()
    if text in NA_TEXT:
        return float("nan")
    text = re.sub(r"^(₹|rs\.?)\s*", "", text)
    text = re.sub(r"/-$", "", text).strip()
    factor = 1
    if text.endswith("k"):
        factor = 1000
        text = text[:-1].strip()
    text = text.replace(",", "")
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", text):
        return float("nan")
    return float(text) * factor


def parse_income(s):
    """Text incomes to floats (missing where the text is not a usable amount)."""
    return pd.Series([_parse_one(v) for v in s], index=s.index, dtype="float64")
