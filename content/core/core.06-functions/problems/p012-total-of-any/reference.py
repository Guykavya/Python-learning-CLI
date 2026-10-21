def total(*numbers):
    """Return the sum of all the numbers passed in (0 if none)."""
    result = 0
    for n in numbers:
        result += n
    return result
