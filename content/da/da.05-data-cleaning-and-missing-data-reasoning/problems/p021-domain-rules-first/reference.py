import pandas as pd


def flag_impossible(df, rules):
    flags = pd.DataFrame(index=df.index)
    counts = {}
    for col, (lo, hi) in rules.items():
        s = df[col]
        bad = pd.Series(False, index=df.index)
        if lo is not None:
            bad = bad | (s < lo).fillna(False).astype(bool)
        if hi is not None:
            bad = bad | (s > hi).fillna(False).astype(bool)
        flags[col] = bad
        counts[col] = int(bad.sum())
    return flags, counts
