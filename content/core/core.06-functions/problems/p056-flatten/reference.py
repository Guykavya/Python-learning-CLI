def flatten(nested):
    """Return a new flat list of the non-list items in nested, in order."""
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result
