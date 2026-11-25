import math


def norm(v):
    total = 0.0
    for x in v:
        total += float(x) * float(x)
    return math.sqrt(total)
