import numpy as np


def running_balance(opening, txns):
    """Balance after each transaction, float64, same length as txns."""
    txns = np.asarray(txns, dtype=float)
    return opening + np.cumsum(txns)


def first_overdraft_day(opening, txns):
    """Index of the first transaction that leaves the balance below 0, or -1."""
    below = running_balance(opening, txns) < 0
    if not below.any():
        return -1
    return int(np.argmax(below))
