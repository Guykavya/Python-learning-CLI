import numpy as np


def tax_vec(incomes):
    """Same as tax_loop, without a loop."""
    x = np.asarray(incomes, dtype=float)
    return np.where(x <= 25_000, 0.0,
                    np.where(x <= 75_000, (x - 25_000) * 0.10, 5_000 + (x - 75_000) * 0.30))


def change_vec(prices, limit):
    """Same as change_loop, without a loop."""
    p = np.asarray(prices, dtype=float)
    return np.clip(np.diff(p), -limit, limit)


def nearest_vec(values, centres):
    """Same as nearest_loop, without a loop over the values."""
    v = np.asarray(values, dtype=float)
    c = np.asarray(centres, dtype=float)
    return np.abs(v[:, None] - c[None, :]).argmin(axis=1)
