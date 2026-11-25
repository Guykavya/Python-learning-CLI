import re
from datetime import datetime

import pandas as pd

FORMATS = [
    (r"[0-9]{4}-[0-9]{2}-[0-9]{2}", "%Y-%m-%d"),
    (r"[0-9]{2}/[0-9]{2}/[0-9]{4}", "%d/%m/%Y"),
    (r"[A-Z][a-z]{2} [0-9]{2}, [0-9]{4}", "%b %d, %Y"),
]


def parse_signup(s):
    """Return (dates, bad): a datetime Series and the sorted list of texts that could not be read."""
    values = []
    bad = set()
    for raw in s:
        if pd.isna(raw):
            values.append(pd.NaT)
            continue
        text = str(raw).strip()
        result = pd.NaT
        for pattern, fmt in FORMATS:
            if re.fullmatch(pattern, text):
                try:
                    result = pd.Timestamp(datetime.strptime(text, fmt))
                except ValueError:
                    pass
                break
        if result is pd.NaT:
            bad.add(text)
        values.append(result)
    return pd.Series(pd.to_datetime(values), index=s.index), sorted(bad)
