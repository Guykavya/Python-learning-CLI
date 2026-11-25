import pandas as pd


def filter_products(df, categories, lo, hi, word):
    """category in categories, lo <= price <= hi, name contains word (any case)."""
    mask = (
        df["category"].isin(categories)
        & df["price"].between(lo, hi)
        & df["name"].str.contains(word, case=False, na=False, regex=False)
    )
    return df[mask]
