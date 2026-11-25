import pandas as pd


def to_wide(long):
    """(store_id, month, sales) -> store_id + one column per sorted month; absent pairs are NaN."""
    # TODO: pivot, reset_index, clear columns.name
    raise NotImplementedError


def to_long(wide):
    """Inverse of to_wide: drop missing cells, sales back to int64, sorted by store and month."""
    # TODO: melt, drop missing sales, cast, sort, fresh index
    raise NotImplementedError
