import numpy as np
import pandas as pd


def simulate_missing(pop, mechanism, rate, rng):
    """Return a copy of pop with some incomes set to NaN, by the mechanism "MCAR", "MAR" or "MNAR"."""
    raise NotImplementedError("a weight per row, probabilities with average `rate`, then rng.random(n) < p")
