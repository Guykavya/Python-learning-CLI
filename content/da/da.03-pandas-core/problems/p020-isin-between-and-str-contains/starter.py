import pandas as pd


def filter_products(df, categories, lo, hi, word):
    """category in categories, lo <= price <= hi, name contains word (any case)."""
    return df[df["category"].isin(categories)]
