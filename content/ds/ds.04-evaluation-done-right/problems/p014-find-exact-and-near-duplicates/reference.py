import pandas as pd


def duplicate_groups(df, cols, round_to=2):
    key = df[list(cols)].copy()
    for c in cols:
        if pd.api.types.is_numeric_dtype(key[c]):
            key[c] = key[c].round(round_to)
    return key.groupby(list(cols), sort=False, dropna=False).ngroup()
