"""A small copy of the chapter's FreshBox factory (section 2.1) for the tests."""
import numpy as np
import pandas as pd

WEEKS = pd.date_range("2023-01-02", "2024-12-30", freq="W-MON")


def make_freshbox(seed=21, n=400):
    rng = np.random.default_rng(seed)
    W = len(WEEKS)
    signup = rng.integers(0, 87, n)
    paid_p = np.where(signup < 75, .35, .55)
    channel = np.where(rng.random(n) < paid_p, "paid", np.where(rng.random(n) < .7, "organic", "referral"))
    plan = rng.choice(["2-meal", "3-meal"], n, p=[.55, .45])
    city = rng.choice(["Metro", "Large", "Small"], n, p=[.45, .35, .2])
    ch_mult = pd.Series(channel).map({"paid": 1.5, "organic": 1.0, "referral": 0.7}).to_numpy()
    sep_week = int((pd.Timestamp("2024-09-02") - WEEKS[0]).days / 7)
    hike_week = int((pd.Timestamp("2024-10-07") - WEEKS[0]).days / 7)
    alive = np.zeros(n, bool)
    churn_idx = np.full(n, -1)
    tenure = np.zeros(n, int)
    late_hist = np.zeros((n, 3), bool)
    rows = []
    for t in range(W):
        alive |= (signup == t)
        idx = np.flatnonzero(alive)
        if len(idx) == 0:
            continue
        late = rng.random(len(idx)) < (0.08 if t < sep_week else 0.20)
        price = np.where(plan[idx] == "2-meal", 599, np.where(t >= hike_week, 934, 849))
        rows.append(pd.DataFrame({"customer_id": idx, "week": WEEKS[t], "tenure_wk": tenure[idx], "late": late, "price": price}))
        late_hist[idx] = np.column_stack([late_hist[idx][:, 1:], late])
        recent_late = late_hist[idx].any(axis=1)
        ten_mult = np.where(tenure[idx] < 8, 1.6, 1.0) * np.exp(-0.01 * np.minimum(tenure[idx], 60))
        hike = ((plan[idx] == "3-meal") & (t >= hike_week)).astype(float)
        hazard = 0.008 * ch_mult[idx] * ten_mult * np.exp(1.1 * recent_late + 0.15 * hike)
        gone = rng.random(len(idx)) < hazard
        churn_idx[idx[gone]] = t
        alive[idx[gone]] = False
        tenure[idx] += 1
    panel = pd.concat(rows, ignore_index=True)
    cw = np.full(n, np.datetime64("NaT", "ns"))
    cw[churn_idx >= 0] = WEEKS.values[churn_idx[churn_idx >= 0]]
    customers = pd.DataFrame({"customer_id": np.arange(n), "signup_week": WEEKS[signup], "channel": channel, "plan": plan,
                              "city": city, "last_week": pd.to_datetime(cw)})
    return customers, panel
