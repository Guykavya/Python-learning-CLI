"""Small helpers for the missing-data simulations of this module (a trimmed copy of the chapter's section 8.2)."""
import numpy as np
import pandas as pd


def make_population(n=6000, seed=5):
    rng = np.random.default_rng(seed)
    edu = rng.choice([8, 10, 12, 14, 16, 18], n, p=[.1, .15, .3, .2, .15, .1])
    age = rng.integers(22, 66, n)
    inc = np.exp(8.6 + 0.12 * edu + 0.008 * (age - 22) + rng.normal(0, 0.35, n)).round(-2)
    return pd.DataFrame({"edu_years": edu, "age": age, "income": inc})


def hide_income(pop, how, rate, seed):
    """Delete incomes from a copy of pop. 'MCAR': a coin flip. 'MAR': under-40s hide twice as often (visible: age)."""
    rng = np.random.default_rng(seed)
    out = pop.copy()
    w = np.ones(len(out)) if how == "MCAR" else np.where(out["age"] < 40, 2.0, 1.0)
    hide = rng.random(len(out)) < np.clip(rate * w / w.mean(), 0, 1)
    out.loc[hide, "income"] = np.nan
    return out
