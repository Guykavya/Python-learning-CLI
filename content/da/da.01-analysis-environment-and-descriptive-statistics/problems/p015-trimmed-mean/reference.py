import math


def trimmed_mean(values, proportion=0.1):
    if not values:
        raise ValueError("empty list")
    if proportion < 0 or proportion >= 0.5:
        raise ValueError("proportion must be at least 0 and below 0.5")
    s = sorted(values)
    k = math.floor(len(s) * proportion)
    kept = s[k:len(s) - k]
    return sum(kept) / len(kept)
