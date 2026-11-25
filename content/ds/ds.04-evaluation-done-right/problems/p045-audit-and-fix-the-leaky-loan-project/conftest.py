import numpy as np
import pandas as pd


def make_loans(n=7000, n_customers=700, seed=3, n_vendor=200):
    r = np.random.default_rng(seed)
    cust_effect = r.normal(0, 1.4, n_customers)               # hidden: some borrowers are just riskier
    cust_birth = r.integers(1950, 2003, n_customers)
    cust_post = r.integers(0, 400, n_customers)
    cid = r.integers(0, n_customers, n)
    day = np.sort(r.integers(0, 730, n))
    income = np.exp(r.normal(10.6, 0.5, n)).round(-2)
    debt_ratio = np.clip(r.beta(2.5, 5, n), 0.02, 0.95).round(3)
    amount = np.exp(r.normal(11.2, 0.6, n)).round(-3)
    score = np.clip(r.normal(650, 70, n), 300, 850).round()
    emp = np.clip(r.gamma(2, 3, n), 0, 40).round(1)
    logit = (-3.4 + 3.0 * (debt_ratio - 0.3) - 0.012 * (score - 650) + 0.35 * (amount / income - 1.0)
             - 0.04 * emp + 0.0012 * day + cust_effect[cid])      # default risk drifts upward over time
    default = (r.random(n) < 1 / (1 + np.exp(-logit))).astype(int)
    df = pd.DataFrame(dict(loan_id=np.arange(n), customer_id=cid, application_day=day, income=income,
                           debt_ratio=debt_ratio, loan_amount=amount, credit_score=score, employment_years=emp,
                           birth_year=cust_birth[cid], postcode=cust_post[cid]))
    for j in range(n_vendor):
        df[f"vendor_{j:03d}"] = r.normal(size=n)                  # anonymous columns with no signal at all
    df["collections_calls"] = np.where(default == 1, r.poisson(3, n), r.poisson(0.05, n))
    df["default"] = default
    dup = df.sample(frac=0.06, random_state=1)                    # the faulty import loaded 6% of rows twice
    return pd.concat([df, dup], ignore_index=True).sort_values(["application_day", "loan_id"], kind="stable").reset_index(drop=True)
