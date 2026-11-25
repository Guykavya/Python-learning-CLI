import numpy as np


def peeking_simulation(n_sims=400, n_per_group=3000, looks=14, p=0.06, seed=3):
    rng = np.random.default_rng(seed)
    a = rng.random((n_sims, n_per_group)) < p
    b = rng.random((n_sims, n_per_group)) < p
    per_look = n_per_group // looks
    ns = per_look * np.arange(1, looks + 1)
    ka = a.cumsum(axis=1)[:, ns - 1]
    kb = b.cumsum(axis=1)[:, ns - 1]
    pp = (ka + kb) / (2 * ns)
    var = pp * (1 - pp) * 2 / ns
    z = np.divide((kb - ka) / ns, np.sqrt(var), out=np.zeros(var.shape), where=var > 0)
    sig = np.abs(z) > 1.96
    return float(sig[:, -1].mean()), float(sig.any(axis=1).mean())
