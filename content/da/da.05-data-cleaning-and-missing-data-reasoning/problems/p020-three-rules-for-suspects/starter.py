import pandas as pd


def flag_iqr(x, k=1.5):
    """True where x is below Q1 - k*IQR or above Q3 + k*IQR."""
    raise NotImplementedError("quartiles, IQR, the two fences")


def flag_z(x, t=3):
    """True where the plain z-score is larger than t in absolute value."""
    raise NotImplementedError("(x - mean) / std")


def flag_mad(x, t=3.5):
    """True where the robust z-score 0.6745 * (x - median) / MAD is larger than t in absolute value."""
    raise NotImplementedError("median and MAD instead of mean and std")
