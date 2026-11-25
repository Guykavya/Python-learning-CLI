import numpy as np
import pandas as pd
import pytest

from solution import opportunity


def make():
    mobile = pd.DataFrame({"device": "mobile", "added_to_cart": [True] * 1000,
                           "started_checkout": [True] * 400 + [False] * 600, "purchased": [True] * 300 + [False] * 700})
    desktop = pd.DataFrame({"device": "desktop", "added_to_cart": [True] * 500,
                            "started_checkout": [True] * 400 + [False] * 100, "purchased": [True] * 380 + [False] * 120})
    noise = pd.DataFrame({"device": "mobile", "added_to_cart": [False] * 300, "started_checkout": [False] * 300, "purchased": [False] * 300})
    return pd.concat([mobile, desktop, noise], ignore_index=True)


def test_plain_numbers():
    r = opportunity(make(), 0.55, n_boot=300)
    assert r["carts"] == 1000, "only mobile sessions with a cart: 1,000 (not the desktop ones, not the sessions without a cart)."
    assert r["now_rate"] == pytest.approx(0.40) and r["pay_rate"] == pytest.approx(0.75), f"now 40%, pay 75%; got {r['now_rate']}, {r['pay_rate']}"
    assert set(r) == {"carts", "now_rate", "pay_rate", "low", "mid", "high"}


def test_point_estimate_and_ordering():
    r = opportunity(make(), 0.55, n_boot=1000)
    assert r["mid"] == pytest.approx(112.5, rel=0.06), f"(0.55 - 0.40) x 1,000 x 0.75 = 112.5 extra purchases; the bootstrap median should be close, got {r['mid']:.1f}"
    assert r["low"] < r["mid"] < r["high"], "the interval brackets the middle value."
    assert r["low"] > 0, "the plausible range here is entirely positive."


def test_target_below_current_rate_is_zero_not_negative():
    r = opportunity(make(), 0.30, n_boot=300)
    assert r["low"] == r["mid"] == r["high"] == 0.0, f"a target below the current rate adds nothing: all zeros, got {r}"


def test_reproducible_and_no_mobile_carts():
    assert opportunity(make(), 0.55, n_boot=200, seed=5) == opportunity(make(), 0.55, n_boot=200, seed=5), "same seed, same answer."
    only_desktop = make()[lambda d: d["device"] == "desktop"]
    with pytest.raises(ValueError, match="no mobile carts"):
        opportunity(only_desktop, 0.55)
