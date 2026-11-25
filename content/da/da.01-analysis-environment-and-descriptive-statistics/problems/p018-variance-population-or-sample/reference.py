import math


def variance(values, ddof):
    if ddof not in (0, 1):
        raise ValueError("ddof must be 0 (population) or 1 (sample)")
    n = len(values)
    if n - ddof < 1:
        raise ValueError(f"need more than {ddof} value(s)")
    m = sum(values) / n
    return sum((x - m) ** 2 for x in values) / (n - ddof)


def stdev(values, ddof):
    return math.sqrt(variance(values, ddof))
