import numpy as np
import pandas as pd
import pytest

from solution import mix_rate_decomposition

B, A = ("2024-01", "2024-03"), ("2024-04", "2024-06")


def block(month, seg, n, churned):
    return pd.DataFrame({"month": pd.Period(month, "M"), "tenure": seg, "churned": np.arange(n) < churned})


def world(nb, cb, na, ca):
    """nb/cb: dict segment -> (rows, churned) before; na/ca after."""
    parts = [block("2024-02", s, nb[s], cb[s]) for s in nb] + [block("2024-05", s, na[s], ca[s]) for s in na]
    return pd.concat(parts, ignore_index=True)


def test_hand_example():
    o = world({"new": 200, "old": 800}, {"new": 20, "old": 24}, {"new": 100, "old": 900}, {"new": 15, "old": 45})
    mix, rate, total = mix_rate_decomposition(o, "tenure", B, A)
    assert (round(mix, 2), round(rate, 2), round(total, 2)) == (-0.85, 2.45, 1.6), f"expected (-0.85, 2.45, 1.60) points, got {(mix, rate, total)}"


def test_pure_mix_change_has_no_rate_effect():
    o = world({"new": 200, "old": 800}, {"new": 20, "old": 40}, {"new": 500, "old": 500}, {"new": 50, "old": 25})
    mix, rate, total = mix_rate_decomposition(o, "tenure", B, A)
    assert abs(rate) < 1e-9, f"the segment rates did not change (10% and 5%): rate effect must be 0, got {rate}"
    assert mix == pytest.approx(total), "with unchanged rates the whole change is mix."


def test_pure_rate_change_has_no_mix_effect():
    o = world({"new": 300, "old": 700}, {"new": 30, "old": 21}, {"new": 300, "old": 700}, {"new": 60, "old": 35})
    mix, rate, total = mix_rate_decomposition(o, "tenure", B, A)
    assert abs(mix) < 1e-9, f"the shares did not change: mix effect must be 0, got {mix}"
    assert rate == pytest.approx(total)


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_effects_add_up(seed):
    rng = np.random.default_rng(seed)
    n = 3000
    o = pd.DataFrame({"month": [pd.Period(m, "M") for m in rng.choice(["2024-01", "2024-02", "2024-04", "2024-05", "2024-07"], n)],
                      "tenure": rng.choice(["0-7", "8-25", "26+"], n), "churned": rng.random(n) < 0.06})
    mix, rate, total = mix_rate_decomposition(o, "tenure", B, A)
    assert abs(mix + rate - total) < 1e-9, f"mix + rate must equal the total change exactly; got {mix} + {rate} vs {total}"
    assert all(isinstance(v, float) for v in (mix, rate, total)), "return plain floats."


def test_missing_segment():
    o = world({"new": 10, "old": 10}, {"new": 1, "old": 1}, {"old": 10}, {"old": 2})
    with pytest.raises(ValueError, match="segment missing in one period: new"):
        mix_rate_decomposition(o, "tenure", B, A)
