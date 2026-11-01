import struct
import sys


def growth_points(n):
    """Lengths at which sys.getsizeof of an appended-to list changes."""
    lst = []
    previous = sys.getsizeof(lst)
    points = []
    for _ in range(n):
        lst.append(None)
        size = sys.getsizeof(lst)
        if size != previous:
            points.append(len(lst))
            previous = size
    return points


def copy_cost(n):
    """Total items copied over all reallocations, if each copies the p - 1 old items."""
    return sum(p - 1 for p in growth_points(n))


def capacity(lst):
    """Number of item slots the list has allocated (used or spare)."""
    return (sys.getsizeof(lst) - sys.getsizeof([])) // struct.calcsize("P")
