def apply_to_all(func, items):
    """Return a new list of func(item) for each item."""
    result = []
    for item in items:
        result.append(func(item))
    return result
