import pandas as pd


def map_regions(s, mapping):
    mapped = s.map(mapping)
    is_unknown = s.notna() & mapped.isna()
    names = mapped.where(~is_unknown, "Other")
    return names, sorted(s[is_unknown].unique().tolist())
