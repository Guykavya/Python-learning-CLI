import math


def summarise(values):
    if not values:
        raise ValueError("empty list")
    ordered = sorted(values)
    n = len(ordered)
    mean = sum(ordered) / n
    if n % 2:
        median = ordered[n // 2]
    else:
        median = (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    if n < 2:
        sd = None
    else:
        sd = math.sqrt(sum((x - mean) ** 2 for x in ordered) / (n - 1))
    return {
        "n": n,
        "mean": mean,
        "median": median,
        "sd": sd,
        "min": ordered[0],
        "max": ordered[-1],
    }
