import pandas as pd


def best_copy(df, key):
    """One row per key: the most complete copy; ties go to the latest updated_at, then to the later row."""
    raise NotImplementedError("count the filled cells of each row, sort, keep the best row of each key")
