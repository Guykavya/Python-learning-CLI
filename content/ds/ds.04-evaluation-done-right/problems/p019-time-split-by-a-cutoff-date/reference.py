import pandas as pd


def time_split(df, date_col, cutoff):
    col = df[date_col]
    cut = pd.Timestamp(cutoff) if pd.api.types.is_datetime64_any_dtype(col) else cutoff
    mask = col < cut
    return df[mask], df[~mask]
