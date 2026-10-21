def limit_calls(func, max_calls):
    """Return a wrapper that forwards its arguments to func for the first max_calls calls, then returns None."""
    used = 0

    def wrapper(*args, **kwargs):
        nonlocal used
        if used >= max_calls:
            return None
        used += 1
        return func(*args, **kwargs)

    return wrapper
