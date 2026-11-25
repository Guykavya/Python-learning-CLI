import numpy as np
import statsmodels.api as sm


def slope_ci_coverage(world, n=50, reps=300, seed=0, robust=False):
    if world not in ("clean", "hetero", "autocorr"):
        raise ValueError(f"unknown world: {world}")
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(reps):
        if world == "clean":
            x = rng.uniform(0, 10, n)
            e = rng.normal(0, 3, n)
        elif world == "hetero":
            x = rng.exponential(3, n)
            e = rng.normal(0, 1, n) * (0.2 + x)
        else:
            x = np.arange(n, dtype=float)
            s = rng.normal(0, 3, n)
            e = np.zeros(n)
            e[0] = s[0]
            for t in range(1, n):
                e[t] = 0.8 * e[t - 1] + s[t]
        y = 1 + 2 * x + e
        model = sm.OLS(y, sm.add_constant(x))
        res = model.fit(cov_type="HC3") if robust else model.fit()
        lo, hi = np.asarray(res.conf_int())[1]
        hits += lo <= 2 <= hi
    return hits / reps
