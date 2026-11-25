import pandas as pd


def store_growth(monthly):
    """Sorted copy with growth_pct per store (NaN for first month and after a zero month)."""
    return monthly.copy()
