from collections import Counter

import pandas as pd


def _counts(df, cols):
    counter = Counter()
    for row in df[cols].itertuples(index=False, name=None):
        counter[tuple(None if pd.isna(v) else v for v in row)] += 1
    return counter


def rows_after_join(a, b, key):
    cols = [key] if isinstance(key, str) else list(key)
    ca, cb = _counts(a, cols), _counts(b, cols)
    return sum(n * cb[k] for k, n in ca.items())
