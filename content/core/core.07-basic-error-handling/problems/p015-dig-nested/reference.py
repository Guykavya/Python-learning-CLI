def dig(data, keys, default=None):
    """Follow keys into nested data; return default if a key or index is missing."""
    try:
        for key in keys:
            data = data[key]
    except LookupError:
        return default
    return data
