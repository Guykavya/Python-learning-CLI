import pandas as pd


def sales_for(df, region, month):
    """Sales of one (region, month) pair as int; 0 if the pair does not exist."""
    multi = df.set_index(["region", "month"])
    try:
        return int(multi.loc[(region, month), "sales"])
    except KeyError:
        return 0


def sales_by_region(df):
    """{region: total sales}, regions sorted."""
    multi = df.set_index(["region", "month"])
    regions = sorted(multi.index.get_level_values("region").unique())
    return {r: int(multi.loc[r, "sales"].sum()) for r in regions}
