import pandas as pd


def weighted_mean(sample_df, value, by, pop_shares):
    """Sum over strata of share * stratum mean. ValueError for missing strata (named) or shares not adding to 1."""
    raise NotImplementedError
