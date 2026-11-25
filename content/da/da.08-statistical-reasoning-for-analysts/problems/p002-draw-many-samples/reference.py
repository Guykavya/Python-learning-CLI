import numpy as np


def sample_means(pop, n, reps, rng):
    pop = np.asarray(pop)
    return np.array([rng.choice(pop, n, replace=False).mean() for _ in range(reps)])
