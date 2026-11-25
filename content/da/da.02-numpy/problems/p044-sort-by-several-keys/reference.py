import numpy as np


def sort_records(names, scores, ages):
    """Row order: score descending, then age ascending, then name ascending."""
    names = np.asarray(names, dtype=str)
    scores = np.asarray(scores, dtype=float)
    ages = np.asarray(ages)
    return np.lexsort((names, ages, -scores))
