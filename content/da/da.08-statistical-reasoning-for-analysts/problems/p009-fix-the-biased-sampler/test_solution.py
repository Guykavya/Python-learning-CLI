import numpy as np
import pandas as pd
from solution import draw


def make_pop(N=5000, seed=0):
    rng = np.random.default_rng(seed)
    day = np.arange(N)
    spend = 4000 - 0.5 * day + rng.normal(0, 600, N)          # older customers spend more
    return pd.DataFrame({"customer_id": np.arange(N), "signup_day": day, "spend": spend})


POP = make_pop()


def test_exactly_n_distinct_rows():
    s = draw(POP, 100, np.random.default_rng(1))
    assert len(s) == 100, f"Return exactly n = 100 rows (you returned {len(s)})."
    assert s["customer_id"].is_unique, "The sample has a customer twice: sample positions without replacement."
    assert list(s.columns) == list(POP.columns), "Keep the same columns as pop."


def test_rows_come_from_pop():
    s = draw(POP, 50, np.random.default_rng(2))
    assert s["customer_id"].isin(POP["customer_id"]).all() and (POP.set_index("customer_id").loc[s["customer_id"], "spend"].to_numpy() == s["spend"].to_numpy()).all()


def test_reproducible_and_uses_rng():
    a = draw(POP, 100, np.random.default_rng(5))["customer_id"].tolist()
    b = draw(POP, 100, np.random.default_rng(5))["customer_id"].tolist()
    c = draw(POP, 100, np.random.default_rng(6))["customer_id"].tolist()
    assert a == b, "Same seed, same sample: use the rng argument."
    assert a != c, "Different seeds must give different samples: your sample is not random: it depends on row order."


def test_unbiased_over_many_seeds():
    est = np.mean([draw(POP, 100, np.random.default_rng(s))["spend"].mean() for s in range(200)])
    truth = POP["spend"].mean()
    assert abs(est - truth) / truth < 0.01, f"On average the sample mean should equal the population mean (within 1%): got {est:.0f} against {truth:.0f}. Your sample is not random: it depends on row order."
