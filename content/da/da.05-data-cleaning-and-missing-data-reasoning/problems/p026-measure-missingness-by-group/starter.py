import pandas as pd


def missing_profile(df, by, col):
    """Per group of `by`: rows, missing, rate of missing values in `col`, sorted by rate (largest first)."""
    raise NotImplementedError("count rows and missing values per group, then rate and sort")
