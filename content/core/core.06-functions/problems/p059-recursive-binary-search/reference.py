def binary_search(items, target, lo=0, hi=None):
    """Return an index of target in sorted items, or -1. Recursive, no slicing."""
    if hi is None:
        hi = len(items)
    if lo >= hi:
        return -1
    mid = (lo + hi) // 2
    if items[mid] == target:
        return mid
    if items[mid] < target:
        return binary_search(items, target, mid + 1, hi)
    return binary_search(items, target, lo, mid)
