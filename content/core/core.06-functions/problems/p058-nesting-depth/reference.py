def depth(data):
    """Return the nesting depth of lists and tuples in data (0 for non-containers)."""
    if not isinstance(data, (list, tuple)):
        return 0
    deepest = 0
    for item in data:
        deepest = max(deepest, depth(item))
    return 1 + deepest
