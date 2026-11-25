import math


def normal_cdf(x, mu=0.0, sigma=1.0):
    """P(X <= x) for X ~ Normal(mu, sigma^2)."""
    raise NotImplementedError


def normal_ppf(q, mu=0.0, sigma=1.0):
    """The x with P(X <= x) = q (bisection); ValueError unless 0 < q < 1."""
    raise NotImplementedError
