import struct
import sys


def growth_points(n):
    """Lengths at which sys.getsizeof of an appended-to list changes."""
    # TODO: append n items one by one and compare sys.getsizeof after each append
    return list(range(1, n + 1))


def copy_cost(n):
    """Total items copied over all reallocations, if each copies the p - 1 old items."""
    # TODO
    return 0


def capacity(lst):
    """Number of item slots the list has allocated (used or spare)."""
    # TODO: (getsizeof(lst) - getsizeof([])) // pointer size
    return len(lst)
