def fallback(default):
    """If the function raises ValueError, return `default` instead."""
    def decorate(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except ValueError:
                return default
        return wrapper
    return decorate


@fallback
def parse_price(text):
    """Turn a price like 'Rs 12.50' into a float."""
    return float(text.replace("Rs", "").strip())
