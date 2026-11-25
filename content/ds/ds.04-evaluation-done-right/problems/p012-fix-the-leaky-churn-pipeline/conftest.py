import numpy as np
import pandas as pd


def make_churn(n=4000, seed=0, leaks=False):
    """Synthetic telecom customers. The true churn rule is known and noisy."""
    r = np.random.default_rng(seed)
    contract = r.choice(["month", "year", "two_year"], n, p=[.55, .25, .20])
    tenure = np.clip(r.gamma(2.2, 12, n), 1, 72).round()
    charge = np.clip(r.normal(65, 22, n), 20, 120).round(2)
    calls = r.poisson(1.2 + 0.03 * (charge - 65) / 10 + 0.6 * (contract == "month"), n)
    autopay = r.random(n) < 0.5
    region = r.choice(["north", "south", "east", "west"], n)
    logit = (-1.6 + 1.1 * (contract == "month") - 0.9 * (contract == "two_year")
             - 0.025 * tenure + 0.018 * (charge - 65) + 0.38 * calls - 0.5 * autopay)
    churn = (r.random(n) < 1 / (1 + np.exp(-logit))).astype(int)
    df = pd.DataFrame(dict(tenure_months=tenure, monthly_charge=charge, support_calls=calls,
                           contract=contract, autopay=autopay.astype(int), region=region,
                           churned=churn))
    if leaks:
        # Written AFTER the customer decided: 92% of churners got an offer, only 4% of stayers.
        df["retention_offer_sent"] = np.where(churn == 1, r.random(n) < 0.92,
                                              r.random(n) < 0.04).astype(int)
    return df

from sklearn.preprocessing import StandardScaler


class RecordingScaler(StandardScaler):
    """A StandardScaler that remembers every row it was fitted on (class-level log, survives cloning)."""
    log = []

    def fit(self, X, y=None, sample_weight=None):
        arr = np.asarray(X, dtype=float)
        RecordingScaler.log.append([row.tobytes() for row in arr])
        return super().fit(X, y, sample_weight)
