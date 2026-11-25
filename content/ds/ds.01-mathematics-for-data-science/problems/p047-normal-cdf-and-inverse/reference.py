import math


def normal_cdf(x, mu=0.0, sigma=1.0):
    return 0.5 * (1.0 + math.erf((x - mu) / (sigma * math.sqrt(2.0))))


def normal_ppf(q, mu=0.0, sigma=1.0):
    if not 0.0 < q < 1.0:
        raise ValueError("q must be strictly between 0 and 1")
    lo, hi = -40.0, 40.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if normal_cdf(mid) < q:
            lo = mid
        else:
            hi = mid
    return mu + sigma * (lo + hi) / 2
