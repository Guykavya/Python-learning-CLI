import pandas as pd


def to_wide(monthly):
    """Long (store_id, month, sales) -> wide: store_id column, then one column per month."""
    # TODO: raise ValueError on repeated (store_id, month) pairs, then pivot, reset_index, clear columns.name
    raise NotImplementedError
