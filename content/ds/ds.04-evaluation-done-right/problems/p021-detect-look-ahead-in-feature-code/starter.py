import numpy as np


def uses_future(feature_fn, series, t):
    """True if feature_fn's value at position t changes when everything after t is removed."""
    raise NotImplementedError
