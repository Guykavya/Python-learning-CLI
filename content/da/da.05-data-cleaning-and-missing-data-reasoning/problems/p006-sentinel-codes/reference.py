import pandas as pd


def replace_sentinels(df, codes):
    """Replace code values by missing values; return (new_frame, count_per_column)."""
    out = df.copy()
    counts = {}
    for col, values in codes.items():
        hit = out[col].isin(values)
        counts[col] = int(hit.sum())
        out[col] = out[col].mask(hit)
    return out, counts
