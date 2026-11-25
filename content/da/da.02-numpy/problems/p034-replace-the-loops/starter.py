import numpy as np


def tax_vec(incomes):
    """Same as tax_loop, without a loop."""
    # TODO: np.where (twice) or np.select
    raise NotImplementedError


def change_vec(prices, limit):
    """Same as change_loop, without a loop."""
    # TODO: np.diff and np.clip
    raise NotImplementedError


def nearest_vec(values, centres):
    """Same as nearest_loop, without a loop over the values."""
    # TODO: a (n, k) table of distances, then argmin along the right axis
    raise NotImplementedError
