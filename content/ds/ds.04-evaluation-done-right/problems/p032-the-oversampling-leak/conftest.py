import numpy as np
import pandas as pd


def make_fraud(n=40000, seed=0):
    r = np.random.default_rng(seed)
    amount = np.exp(r.normal(3.6, 1.1, n))                        # skewed, in currency units
    hour = r.integers(0, 24, n)
    tx_24h = r.poisson(2.0, n)
    new_device = (r.random(n) < 0.10).astype(int)
    country_mismatch = (r.random(n) < 0.06).astype(int)
    logit = (-11.4 + 1.1 * np.log(amount) + 2.0 * new_device + 2.4 * country_mismatch
             + 0.3 * tx_24h + 1.2 * ((hour < 5) | (hour > 22)))
    fraud = (r.random(n) < 1 / (1 + np.exp(-logit))).astype(int)
    return pd.DataFrame(dict(amount=amount, hour=hour, tx_24h=tx_24h, new_device=new_device, country_mismatch=country_mismatch, fraud=fraud))
