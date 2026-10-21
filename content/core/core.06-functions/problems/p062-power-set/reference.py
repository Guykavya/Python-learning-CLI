def subsets(items, *, max_size=None):
    """Return every subset of items (as lists, in item order), optionally only up to max_size items."""
    if not items:
        return [[]]
    first = items[0]
    without = subsets(items[1:], max_size=max_size)
    with_first = [[first] + s for s in without if max_size is None or len(s) < max_size]
    return without + with_first
