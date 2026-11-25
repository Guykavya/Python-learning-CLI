import pandas as pd


def price_of(s, label):
    """Price of the product with id `label`."""
    return float(s[label])


def nth_price(s, n):
    """Price at position n (0 = first row, -1 = last row)."""
    return float(s[n])
