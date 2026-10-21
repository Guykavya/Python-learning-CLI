def to_int(text, default=0):
    """Return int(text), or default if text is not a whole number."""
    try:
        return int(text)
    except ValueError:
        return default
