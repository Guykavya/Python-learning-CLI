import numpy as np


def simulate_rolls(n, rng):
    """Counts of faces 1..6 in n rolls made with the Generator rng."""
    rolls = rng.integers(1, 7, size=n)
    return np.bincount(rolls, minlength=7)[1:]
