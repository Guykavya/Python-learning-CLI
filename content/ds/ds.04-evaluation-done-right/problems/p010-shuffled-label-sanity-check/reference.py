import numpy as np


def shuffled_label_check(evaluate, y, repeats=5, seed=0):
    rng = np.random.default_rng(seed)
    y = np.asarray(y)
    scores = [float(evaluate(rng.permutation(y))) for _ in range(repeats)]
    return float(np.mean(scores)), float(np.std(scores))
