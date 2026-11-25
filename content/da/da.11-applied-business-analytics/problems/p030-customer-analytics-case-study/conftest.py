"""Small test world for the ShopNest case study (the course data are much bigger)."""
import re
from dataclasses import dataclass

import numpy as np
import pandas as pd


def make_data(seed=0, lift=0.012, gap=0.21, n_exp=4000, n_sess=3000, n_cus=600):
    rng = np.random.default_rng(seed)
    variant = np.repeat(["A", "B"], n_exp)
    converted = rng.random(2 * n_exp) < np.where(variant == "B", 0.06 + lift, 0.06)
    exp = pd.DataFrame({"variant": variant, "converted": converted, "revenue": np.where(converted, rng.gamma(4, 180, 2 * n_exp), 0.0).round(0)})
    device = rng.choice(["mobile", "desktop"], n_sess, p=[0.65, 0.35])
    cart = rng.random(n_sess) < 0.35
    checkout = cart & (rng.random(n_sess) < np.where(device == "mobile", 0.66 - gap, 0.66))
    buy = checkout & (rng.random(n_sess) < 0.72)
    sessions = pd.DataFrame({"device": device, "added_to_cart": cart, "started_checkout": checkout, "purchased": buy})
    channel = rng.choice(["email", "organic", "paid", "referral"], n_cus, p=[0.15, 0.40, 0.35, 0.10])
    first = pd.Timestamp("2023-01-01") + pd.to_timedelta(rng.integers(0, 700, n_cus), unit="D")
    p_rep = pd.Series(channel).map({"email": 0.55, "organic": 0.35, "paid": 0.22, "referral": 0.60}).to_numpy()
    asof = pd.Timestamp("2024-12-31")
    rows = []
    for i in range(n_cus):
        rows.append((i, first[i], float(round(rng.gamma(4, 150)))))
        for _ in range(rng.poisson(2 * p_rep[i])):
            d = first[i] + pd.Timedelta(days=int(rng.integers(0, 300)))
            if d <= asof:
                rows.append((i, d, float(round(rng.gamma(4, 150)))))
    orders = pd.DataFrame(rows, columns=["customer_id", "order_date", "amount"])
    customers = pd.DataFrame({"customer_id": np.arange(n_cus), "first_order": first, "channel": channel})
    return {"exp": exp, "sessions": sessions, "customers": customers, "orders": orders, "asof": asof}
