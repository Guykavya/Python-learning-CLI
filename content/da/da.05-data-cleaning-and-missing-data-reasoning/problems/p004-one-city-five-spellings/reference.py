import pandas as pd


def standardise_city(s, mapping):
    """Return (clean, unmapped): canonical names, and the sorted keys no mapping rule covered."""
    key = (s.str.strip().str.rstrip(".").str.strip()
            .str.replace(r"\s+", " ", regex=True).str.casefold())
    clean = key.map(mapping)
    unmapped = sorted(set(key[key.notna() & clean.isna()]))
    return clean, unmapped
