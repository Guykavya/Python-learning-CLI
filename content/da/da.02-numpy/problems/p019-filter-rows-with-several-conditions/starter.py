import numpy as np


def select_rows(table, col, lo, hi, exclude=None):
    """Rows with lo <= table[:, col] <= hi; if exclude is a column index, drop rows where that column is not 0."""
    # TODO
    raise NotImplementedError


def outside_rows(table, col, lo, hi):
    """Rows with table[:, col] < lo or > hi."""
    # TODO
    raise NotImplementedError
