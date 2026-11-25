import numpy as np


def running_balance(opening, txns):
    """Balance after each transaction, float64, same length as txns."""
    # TODO: one line with np.cumsum
    raise NotImplementedError


def first_overdraft_day(opening, txns):
    """Index of the first transaction that leaves the balance below 0, or -1."""
    # TODO: a mask, then .any() and argmax
    raise NotImplementedError
