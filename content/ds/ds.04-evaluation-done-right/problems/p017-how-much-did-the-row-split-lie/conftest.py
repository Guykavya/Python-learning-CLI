import numpy as np
import pandas as pd


def make_patients(n_patients=80, visits=15, seed=0):
    r = np.random.default_rng(seed)
    pid = np.repeat(np.arange(n_patients), visits)
    finger = r.normal(0, 1, (n_patients, 4))                 # stable personal traits
    risk = r.normal(0, 1.6, n_patients)                      # personal tendency (hidden)
    symptom = r.normal(0, 1, n_patients * visits)
    logit = risk[pid] + 0.6 * symptom
    y = (r.random(n_patients * visits) < 1 / (1 + np.exp(-logit))).astype(int)
    X = np.column_stack([finger[pid] + r.normal(0, 0.05, (n_patients * visits, 4)), symptom])
    cols = ["trait_a", "trait_b", "trait_c", "trait_d", "symptom_score"]
    return pd.DataFrame(X, columns=cols), y, pid
