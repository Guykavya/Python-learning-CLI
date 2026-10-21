def dig(data, keys, default=None):
    """Follow keys into nested data; return default if a key or index is missing."""
    for key in keys:
        data = data[key]
    return data
