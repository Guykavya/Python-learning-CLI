import pandas as pd


def flag_iqr(x, k=1.5):
    """True where x is below Q1 - k*IQR or above Q3 + k*IQR."""
    q1, q3 = x.quantile([0.25, 0.75])
    spread = q3 - q1
    return (x < q1 - k * spread) | (x > q3 + k * spread)


def flag_z(x, t=3):
    """True where the plain z-score is larger than t in absolute value."""
    return ((x - x.mean()) / x.std()).abs() > t


def flag_mad(x, t=3.5):
    """True where the robust z-score 0.6745 * (x - median) / MAD is larger than t in absolute value."""
    med = x.median()
    mad = (x - med).abs().median()
    if pd.isna(mad) or mad == 0:
        return pd.Series(False, index=x.index)
    return (0.6745 * (x - med) / mad).abs() > t
