n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]


def at_most(m):
    """Number of subarrays with at most m distinct values."""
    # TODO: sliding window with a dictionary of counts
    return 0


print(at_most(k) - at_most(k - 1))
