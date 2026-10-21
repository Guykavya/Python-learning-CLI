def safe_divide(a, b):
    """Return a / b, or None if b is zero."""
    try:
        return a / b
    except ZeroDivisionError:
        return None
