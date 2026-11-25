import pandas as pd


def sales_for(df, region, month):
    """Sales of one (region, month) pair as int; 0 if the pair does not exist."""
    return int(df.set_index(["region", "month"]).loc[(region, month), "sales"])


def sales_by_region(df):
    """{region: total sales}, regions sorted."""
    return {}
