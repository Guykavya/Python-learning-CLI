"""Measure how the cost of a container operation grows with the container's size."""

import timeit
from collections import deque


# ---------------------------------------------------------------- one operation each,
# every function leaves the container the same size it found it


def push_pop_end(container):
    container.append(0)
    container.pop()


def push_pop_front(container):
    container.insert(0, 0)
    container.pop(0)


def push_pop_left(container):
    container.appendleft(0)
    container.popleft()


def search_missing(container):
    return -1 in container


# ---------------------------------------------------------------- measuring


def time_per_call(op, n, factory=list, number=200, repeat=5):
    """Seconds for ONE call of op on a container of n items: the best of `repeat` timings."""
    container = factory(range(n))
    best = min(timeit.repeat(lambda: op(container), number=number, repeat=repeat))
    return best / number


def measure(op, sizes, factory=list, number=200, repeat=5):
    """{n: seconds per call} for every n in sizes."""
    return {n: time_per_call(op, n, factory, number, repeat) for n in sizes}


def growth_kind(t_small, t_large, threshold=5.0):
    """'linear' if the large size is at least `threshold` times slower, else 'constant'."""
    return "linear" if t_large / t_small >= threshold else "constant"


def classify(op, factory=list, small=1_000, large=100_000, number=200, repeat=5):
    """Time op at two sizes and say whether its cost is constant or grows with n."""
    times = measure(op, [small, large], factory, number, repeat)
    return growth_kind(times[small], times[large])
