import numpy as np


def influential_points(result, threshold=None):
    n = int(result.nobs)
    if threshold is None:
        threshold = 4 / n
    cooks = np.asarray(result.get_influence().cooks_distance[0])
    order = np.argsort(-cooks)
    return [int(i) for i in order if cooks[i] > threshold]
