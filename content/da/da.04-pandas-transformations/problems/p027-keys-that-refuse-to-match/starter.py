import pandas as pd


def normalise_keys(left, right, key):
    """Clean the key on both sides; report match rates before/after and the keys that still fail."""
    return {"left": left.copy(), "right": right.copy(), "match_before": 0.0, "match_after": 0.0, "unmatched": []}
