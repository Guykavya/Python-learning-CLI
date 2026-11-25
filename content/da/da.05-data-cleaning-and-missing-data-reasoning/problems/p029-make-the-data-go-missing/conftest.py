"""Small helpers for the missing-data simulations of this module (a trimmed copy of the chapter's section 8.2)."""
import numpy as np
import pandas as pd


def make_population(n=6000, seed=5):
    rng = np.random.default_rng(seed)
    edu = rng.choice([8, 10, 12, 14, 16, 18], n, p=[.1, .15, .3, .2, .15, .1])
    age = rng.integers(22, 66, n)
    inc = np.exp(8.6 + 0.12 * edu + 0.008 * (age - 22) + rng.normal(0, 0.35, n)).round(-2)
    return pd.DataFrame({"edu_years": edu, "age": age, "income": inc})
