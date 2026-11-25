import math


def skewness(values):
    n = len(values)
    if n < 3:
        raise ValueError("need at least 3 values")
    m = sum(values) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in values) / n)
    if sd == 0:
        raise ValueError("all values are equal: skewness is undefined")
    return sum(((x - m) / sd) ** 3 for x in values) / n
