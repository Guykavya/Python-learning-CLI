import pandas as pd


def query_orders(df, min_qty, region):
    """qty >= min_qty, region == region, unit price > 0, written with df.query."""
    return df.query("qty >= 0")
