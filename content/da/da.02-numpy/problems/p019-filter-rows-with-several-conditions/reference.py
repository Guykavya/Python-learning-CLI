import numpy as np


def select_rows(table, col, lo, hi, exclude=None):
    values = table[:, col]
    keep = (values >= lo) & (values <= hi)
    if exclude is not None:
        keep = keep & ~(table[:, exclude] != 0)
    return table[keep]


def outside_rows(table, col, lo, hi):
    values = table[:, col]
    return table[(values < lo) | (values > hi)]
