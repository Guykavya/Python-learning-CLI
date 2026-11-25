import numpy as np
import pandas as pd
import pytest

from solution import step_rates

STEPS = ["view", "cart"]


def make():
    mobile = pd.DataFrame({"device": "mobile", "view": [True] * 60 + [False] * 40, "cart": [True] * 30 + [False] * 70})
    desktop = pd.DataFrame({"device": "desktop", "view": [True] * 8 + [False] * 2, "cart": [True] * 4 + [False] * 6})
    return pd.concat([mobile, desktop], ignore_index=True)


def test_columns_order_and_counts():
    t = step_rates(make(), "device", STEPS)
    assert list(t.columns) == ["device", "step", "n_prev", "n", "rate %", "CI low", "CI high"], f"columns, got {list(t.columns)}"
    assert list(zip(t["device"], t["step"])) == [("desktop", "view"), ("desktop", "cart"), ("mobile", "view"), ("mobile", "cart")], "segments ascending, steps in the given order."
    assert t["n_prev"].tolist() == [10, 8, 100, 60] and t["n"].tolist() == [8, 4, 60, 30], "n_prev is the previous step (all sessions for the first step)."
    assert t["rate %"].tolist() == pytest.approx([80.0, 50.0, 60.0, 50.0])


def test_wilson_limits():
    t = step_rates(make(), "device", STEPS).set_index(["device", "step"])
    row = t.loc[("mobile", "view")]
    assert (round(row["CI low"], 1), round(row["CI high"], 1)) == (50.2, 69.1), f"Wilson 95% interval for 60 of 100: 50.2 to 69.1 percent, got {row['CI low']:.1f} to {row['CI high']:.1f}"
    small = t.loc[("desktop", "view")]
    assert 0 <= small["CI low"] < small["rate %"] < small["CI high"] <= 100, "a Wilson interval stays inside 0 to 100 even for 8 of 10."


def test_empty_previous_step_gives_nan_not_a_crash():
    df = pd.DataFrame({"device": ["mobile"] * 5, "view": [False] * 5, "cart": [False] * 5})
    t = step_rates(df, "device", STEPS)
    assert t.loc[0, "rate %"] == 0.0, "0 of 5 viewed: rate 0."
    assert t.loc[1, ["rate %", "CI low", "CI high"]].isna().all(), "no sessions viewed: the cart rate is undefined (NaN)."
    assert t.loc[1, "n_prev"] == 0
