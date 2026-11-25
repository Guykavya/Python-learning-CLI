import numpy as np
import pandas as pd


def pooled_retention(active, sizes, ks):
    """Series indexed by ks: sum of active / sum of sizes over the cohorts that reached month k (NaN if none)."""
    raise NotImplementedError
