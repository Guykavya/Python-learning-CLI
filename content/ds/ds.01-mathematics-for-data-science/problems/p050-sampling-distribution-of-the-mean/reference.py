import numpy as np


def sample_means(draw, n, reps, seed=0):
    rng = np.random.default_rng(seed)
    return np.asarray(draw(rng, (reps, n))).mean(axis=1)
