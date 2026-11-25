import numpy as np


def customer_changes(jan_ids, feb_ids):
    """(new, lost, kept): sorted unique ids, by set operations."""
    jan = np.asarray(jan_ids)
    feb = np.asarray(feb_ids)
    new = np.setdiff1d(feb, jan)
    lost = np.setdiff1d(jan, feb)
    kept = np.intersect1d(jan, feb)
    return new, lost, kept
