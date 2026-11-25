import numpy as np


def best_of_many_optimism(n_models, seed):
    rng = np.random.default_rng(seed)
    X_val = rng.normal(size=(100, 10))
    y_val = rng.integers(0, 2, 100)
    X_test = rng.normal(size=(1000, 10))
    y_test = rng.integers(0, 2, 1000)
    best_acc, best_w = -1.0, None
    for _ in range(n_models):
        w = rng.normal(size=10)
        acc = float(np.mean(((X_val @ w) > 0).astype(int) == y_val))
        if acc > best_acc:
            best_acc, best_w = acc, w
    test_acc = float(np.mean(((X_test @ best_w) > 0).astype(int) == y_test))
    return best_acc, test_acc
