import pandas as pd


def query_orders(df, min_qty, region):
    """qty >= min_qty, region == region, unit price > 0, written with df.query."""
    return df.query("qty >= @min_qty and region == @region and `unit price` > 0")
