import numpy as np
import pandas as pd


def make_sales(n=730, seed=0):
    r = np.random.default_rng(seed)
    t = np.arange(n)
    dow = t % 7
    promo = (r.random(n) < 0.10).astype(int)
    noise = np.zeros(n)
    for i in range(1, n):                                  # noise that persists for a few days
        noise[i] = 0.6 * noise[i - 1] + r.normal(0, 6)
    y = 100 + 0.25 * t + 15 * np.sin(2 * np.pi * dow / 7) + 30 * promo + noise
    return pd.DataFrame({"day": t, "dow": dow, "promo": promo, "sales": y})
