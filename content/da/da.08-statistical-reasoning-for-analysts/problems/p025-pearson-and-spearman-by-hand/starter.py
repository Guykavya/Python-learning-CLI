import numpy as np
from scipy.stats import rankdata


def pearson(x, y):
    """Pearson correlation; ValueError('r is undefined when one variable does not vary') for a constant variable."""
    raise NotImplementedError


def spearman(x, y):
    """Pearson correlation of the ranks (ties share the average rank)."""
    raise NotImplementedError
