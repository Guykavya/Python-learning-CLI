def factorial(n):
    """Return n! for n >= 0, computed recursively."""
    if n == 0:
        return 1
    return n * factorial(n - 1)
