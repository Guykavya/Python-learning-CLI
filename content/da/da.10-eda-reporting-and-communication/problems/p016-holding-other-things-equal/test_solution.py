import numpy as np
import pandas as pd
import pytest

from solution import late_effect

TRUE_OR = 2.0


def world(seed, n=20000):
    rng = np.random.default_rng(seed)
    new = rng.random(n) < 0.3
    late = rng.random(n) < np.where(new, 0.4, 0.1)                     # new customers get more late boxes (the confounding)
    p = 1 / (1 + np.exp(-(-3 + np.log(TRUE_OR) * late + 1.5 * new)))   # true effect of late: odds ratio 2
    churn = rng.random(n) < p
    return pd.DataFrame({"churn": churn.astype(int), "late": late.astype(int), "new": new.astype(int)})


@pytest.mark.parametrize("seed", [0, 2, 3])
def test_adjusted_interval_contains_the_truth(seed):
    r = late_effect(world(seed))
    assert r["ci_low"] < TRUE_OR < r["ci_high"], f"the adjusted 95% CI should contain the true odds ratio 2.0, got {r['ci_low']:.2f} to {r['ci_high']:.2f} (did you include new in the model?)"
    assert r["ci_low"] < r["odds_ratio"] < r["ci_high"], "the estimate lies inside its interval (exponentiate both)."


def test_naive_is_further_from_the_truth():
    r = late_effect(world(0))
    assert r["naive_odds_ratio"] > 2.8, f"without adjusting, late also carries the 'new customer' effect: about 3.4, got {r['naive_odds_ratio']:.2f}"
    assert abs(r["naive_odds_ratio"] - TRUE_OR) > abs(r["odds_ratio"] - TRUE_OR), "the adjusted estimate must be closer to the truth than the naive one."


def test_naive_on_a_hand_table():
    df = pd.DataFrame({"late": [1] * 10 + [0] * 10, "new": [0, 1] * 10,
                       "churn": [1, 1, 1, 1, 0, 0, 0, 0, 0, 0] + [1, 1, 0, 0, 0, 0, 0, 0, 0, 0]})
    r = late_effect(df)
    assert r["naive_odds_ratio"] == pytest.approx((4 / 6) / (2 / 8)), "naive OR = (churners/stayers among late) / (churners/stayers among not late) = (4/6)/(2/8)."


def test_plain_floats():
    r = late_effect(world(1, n=5000))
    assert set(r) == {"odds_ratio", "ci_low", "ci_high", "naive_odds_ratio"}, f"keys, got {sorted(r)}"
    assert all(type(v) is float for v in r.values()), "return plain floats."
