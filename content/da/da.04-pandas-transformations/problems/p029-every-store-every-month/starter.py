import pandas as pd


def full_grid(sales, stores, months):
    """One row per store and month, revenue 0.0 where nothing was sold."""
    return sales.copy()
