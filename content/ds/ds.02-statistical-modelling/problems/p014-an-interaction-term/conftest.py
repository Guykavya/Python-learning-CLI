import numpy as np
import pandas as pd

def make_wages(n=400, seed=11):
    rng = np.random.default_rng(seed)
    experience = rng.integers(0, 31, size=n)
    education = rng.choice(["school", "degree", "masters"], size=n, p=[0.4, 0.4, 0.2])
    city = rng.choice(["Pune", "Delhi", "Mumbai"], size=n, p=[0.4, 0.35, 0.25])
    log_wage = (10.2 + 0.025 * experience
                + 0.18 * (education == "degree") + 0.40 * (education == "masters")
                + 0.10 * (city == "Delhi") + 0.22 * (city == "Mumbai")
                + 0.01 * experience * (education == "masters")
                + rng.normal(0, 0.25, size=n))
    return pd.DataFrame({"wage": np.exp(log_wage).round(0), "experience": experience,
                         "education": education, "city": city})
