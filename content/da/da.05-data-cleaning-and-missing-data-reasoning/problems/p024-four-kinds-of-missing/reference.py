import pandas as pd


def to_missing(df, tokens=("", "NA", "n/a", "-")):
    out = df.copy()
    words = {t.strip().lower() for t in tokens}
    counts = {}
    for col in out.columns:
        s = out[col]
        if pd.api.types.is_numeric_dtype(s) or pd.api.types.is_datetime64_any_dtype(s):
            counts[col] = 0
            continue
        hit = s.notna() & s.astype(str).str.strip().str.lower().isin(words)
        out[col] = s.mask(hit)
        counts[col] = int(hit.sum())
    return out, counts
