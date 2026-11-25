import math


def weighted_mean(values, weights):
    if not values or len(values) != len(weights):
        raise ValueError("need equal, non-empty lists")
    if any(w < 0 for w in weights) or sum(weights) == 0:
        raise ValueError("weights must be non-negative and not all zero")
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)


def geometric_mean(values):
    if not values or any(v <= 0 for v in values):
        raise ValueError("need a non-empty list of positive numbers")
    return math.exp(sum(math.log(v) for v in values) / len(values))


def harmonic_mean(values):
    if not values or any(v <= 0 for v in values):
        raise ValueError("need a non-empty list of positive numbers")
    return len(values) / sum(1 / v for v in values)
