import pandas as pd


def fill_gaps(s, how):
    if how == "drop":
        return s.dropna()
    if how == "zero":
        return s.fillna(0)
    if how == "ffill":
        return s.ffill()
    if how == "interpolate":
        return s.interpolate()
    if how == "median":
        return s.fillna(s.median())
    raise ValueError(f"unknown strategy {how!r}")
