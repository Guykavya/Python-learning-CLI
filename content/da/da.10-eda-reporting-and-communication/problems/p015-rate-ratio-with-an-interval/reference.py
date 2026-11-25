import math


def rate_ratio(e1, n1, e0, n0):
    if e1 > n1 or e0 > n0:
        raise ValueError("events cannot exceed the group size")
    if e1 <= 0 or e0 <= 0:
        raise ValueError("need at least one event in each group")
    rr = (e1 / n1) / (e0 / n0)
    se = math.sqrt(1 / e1 - 1 / n1 + 1 / e0 - 1 / n0)
    return float(rr), float(rr * math.exp(-1.96 * se)), float(rr * math.exp(1.96 * se))
