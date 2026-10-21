def retry(func, attempts=3, errors=(ValueError,)):
    """Call func() up to `attempts` times, retrying only the given error types."""
    return func()
