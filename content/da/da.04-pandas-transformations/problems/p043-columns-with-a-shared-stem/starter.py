import pandas as pd


def yearly_long(df):
    """store_id + sales_<year>/units_<year> columns -> rows (store_id, year, sales, units)."""
    # TODO: pd.wide_to_long(..., stubnames=..., i=..., j=..., sep=...), reset_index, sort
    raise NotImplementedError
