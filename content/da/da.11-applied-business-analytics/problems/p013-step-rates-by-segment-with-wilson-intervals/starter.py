import numpy as np
import pandas as pd
from scipy import stats


def step_rates(df, by, steps):
    """One row per segment and step: n_prev, n, rate %, Wilson CI low and high (percent); NaN when n_prev is 0."""
    raise NotImplementedError
