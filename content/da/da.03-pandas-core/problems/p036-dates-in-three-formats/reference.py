import pandas as pd


def parse_dates(s, formats):
    text = s.astype("string").str.strip()
    parsed = pd.Series(pd.NaT, index=s.index, dtype="datetime64[us]")
    for f in formats:
        parsed = parsed.fillna(pd.to_datetime(text, format=f, errors="coerce"))
    unparsed = s[parsed.isna() & s.notna()].tolist()
    return parsed, unparsed
