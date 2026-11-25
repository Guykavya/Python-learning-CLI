import math


def summarise(values):
    """Return n, mean, median, sd (sample), min and max of a list of numbers."""
    if not values:
        raise ValueError("empty list")
    values.sort()
    n = len(values)
    mean = sum(values) / n
    if n % 2:
        median = values[n // 2]
    else:
        median = (values[n // 2] + values[n // 2 + 1]) / 2
    variance = sum((x - mean) ** 2 for x in values) / n
    return {
        "n": n,
        "mean": mean,
        "median": median,
        "sd": math.sqrt(variance),
        "min": values[0],
        "max": values[-1],
    }
