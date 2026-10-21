from functools import reduce


def product(numbers):
    """Return the product of numbers (1 for an empty list), using reduce."""
    return reduce(lambda acc, n: acc * n, numbers, 1)
