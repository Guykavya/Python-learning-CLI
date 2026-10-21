def sum_digits(n):
    """Return the sum of the decimal digits of n (sign ignored), recursively."""
    if n < 0:
        return sum_digits(-n)
    if n < 10:
        return n
    return n % 10 + sum_digits(n // 10)
