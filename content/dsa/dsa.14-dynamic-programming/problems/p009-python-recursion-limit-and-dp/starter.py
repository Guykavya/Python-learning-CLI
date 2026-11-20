import functools


@functools.cache
def min_steps(n):
    """Fewest moves (-1, /2 if even, /3 if divisible by 3) from n to 1. Must work for n up to 2 * 10**5."""
    if n == 1:
        return 0
    best = min_steps(n - 1) + 1
    if n % 2 == 0:
        best = min(best, min_steps(n // 2) + 1)
    if n % 3 == 0:
        best = min(best, min_steps(n // 3) + 1)
    return best
