"""Measure how the cost of a container operation grows with the container's size."""

import timeit
from collections import deque


def push_pop_end(container):
    """append one item, then pop it (the container ends unchanged)."""
    # TODO


def push_pop_front(container):
    """insert(0, ...) one item, then pop(0) it."""
    # TODO


def push_pop_left(container):
    """deque: appendleft one item, then popleft it."""
    # TODO


def search_missing(container):
    """Return whether -1 is in the container."""
    return False


def time_per_call(op, n, factory=list, number=200, repeat=5):
    """Seconds for ONE call of op on a container of n items: the best of `repeat` timings."""
    return 1.0


def measure(op, sizes, factory=list, number=200, repeat=5):
    """{n: seconds per call} for every n in sizes."""
    return {}


def growth_kind(t_small, t_large, threshold=5.0):
    """'linear' if the large size is at least `threshold` times slower, else 'constant'."""
    return "constant"


def classify(op, factory=list, small=1_000, large=100_000, number=200, repeat=5):
    """Time op at two sizes and say whether its cost is constant or grows with n."""
    return "constant"
