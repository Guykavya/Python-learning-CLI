import pandas as pd


def to_long(wide):
    """Wide (store_id + one column per month) -> long (store_id, month, sales), sorted by store and month."""
    # TODO: melt with id_vars, var_name and value_name, then sort and reset the index
    raise NotImplementedError
