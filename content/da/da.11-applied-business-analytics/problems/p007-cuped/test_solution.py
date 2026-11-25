import numpy as np
import pandas as pd
import pytest

from solution import cuped


def make(seed=0, n=8000, lift=0.12, rho_strength=1.0):
    rng = np.random.default_rng(seed)
    variant = rng.random(n) < 0.5
    z = rng.normal(0, 1, n)
    pre = rng.poisson(np.exp(0.9 * z))
    p = 1 / (1 + np.exp(-(-3.1 + rho_strength * z + lift * variant)))
    return pd.DataFrame({"variant": np.where(variant, "B", "A"), "pre_orders_90d": pre, "converted": rng.random(n) < p})


def test_variance_shrinks_by_one_minus_r2():
    df = make()
    adj, theta, r2 = cuped(df)
    y = df["converted"].astype(float).to_numpy()
    assert np.var(adj, ddof=1) == pytest.approx((1 - r2) * np.var(y, ddof=1), rel=1e-9), "the adjusted variance is (1 - r2) times the variance of y."
    assert r2 > 0.02, "the pre-experiment orders do predict conversion in this world."


def test_mean_is_unchanged_and_order_kept():
    df = make(1)
    adj, theta, r2 = cuped(df)
    assert adj.shape == (len(df),) and isinstance(adj, np.ndarray), "return a NumPy array, one value per row."
    assert adj.mean() == pytest.approx(df["converted"].mean(), abs=1e-12), "subtract theta * (x - mean(x)): the mean of the outcome must not move."


def test_difference_between_groups_barely_changes_and_interval_narrows():
    df = make(2)
    adj, _, _ = cuped(df)
    d = lambda v: v[(df["variant"] == "B").to_numpy()].mean() - v[(df["variant"] == "A").to_numpy()].mean()
    se = lambda v: np.sqrt(v[(df["variant"] == "A").to_numpy()].var(ddof=1) / (df["variant"] == "A").sum() + v[(df["variant"] == "B").to_numpy()].var(ddof=1) / (df["variant"] == "B").sum())
    raw = df["converted"].astype(float).to_numpy()
    assert abs(d(adj) - d(raw)) < 2 * se(raw), "the adjusted difference stays within the noise of the raw one."
    assert se(adj) < se(raw), "CUPED gives a smaller standard error."


def test_hand_cases():
    d = pd.DataFrame({"y": [2.0, 4.0, 6.0, 8.0], "x": [1.0, 2.0, 3.0, 4.0]})
    adj, theta, r2 = cuped(d, "y", "x")
    assert theta == pytest.approx(2.0) and r2 == pytest.approx(1.0), "y = 2x: theta = 2, r2 = 1."
    assert np.allclose(adj, 5.0), "a perfect covariate removes all variation: every adjusted value is the mean of y."


def test_unrelated_covariate_changes_nothing():
    rng = np.random.default_rng(3)
    d = pd.DataFrame({"y": rng.normal(10, 2, 5000), "x": rng.normal(0, 1, 5000)})
    adj, theta, r2 = cuped(d, "y", "x")
    assert abs(theta) < 0.15 and r2 < 0.005, f"no relation: theta near 0 and r2 near 0, got {theta:.3f}, {r2:.4f}"
    assert np.allclose(adj, d["y"], atol=0.5), "nothing is removed when x tells nothing about y."
