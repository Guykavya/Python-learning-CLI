import pandas as pd


def to_missing(df, tokens=("", "NA", "n/a", "-")):
    """Return (clean, counts): blanks, whitespace and tokens become real missing values."""
    raise NotImplementedError("strip, lower-case, compare with the tokens, mask; count per column")
