import pandas as pd


def clean(s):
    return s.astype(str).str.strip().str.upper()


def normalise_keys(left, right, key):
    """Clean the key on both sides; report match rates before/after and the keys that still fail."""
    before = float(left[key].isin(right[key]).mean())
    l2 = left.assign(**{key: clean(left[key])})
    r2 = right.assign(**{key: clean(right[key])})
    found = l2[key].isin(r2[key])
    after = float(found.mean())
    unmatched = sorted(l2.loc[~found, key].unique().tolist())
    return {"left": l2, "right": r2, "match_before": before, "match_after": after, "unmatched": unmatched}
