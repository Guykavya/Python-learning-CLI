import pandas as pd


def fill_price_by_category(products):
    """Return (filled copy, sorted list of categories with no known price)."""
    median = products.groupby("category")["list_price"].transform("median")
    filled = products.assign(list_price=products["list_price"].fillna(median))
    known = products.groupby("category")["list_price"].count()
    unfilled = sorted(known[known == 0].index.tolist())
    return filled, unfilled
