def retry(func, attempts=3, errors=(ValueError,)):
    """Call func() up to `attempts` times, retrying only the given error types."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    last_error = None
    for _ in range(attempts):
        try:
            return func()
        except errors as e:
            last_error = e
    raise last_error
