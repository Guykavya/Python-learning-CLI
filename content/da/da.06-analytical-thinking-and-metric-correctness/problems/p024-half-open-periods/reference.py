import pandas as pd


def in_period(s, start, end):
    return (s >= pd.Timestamp(start)) & (s < pd.Timestamp(end))
