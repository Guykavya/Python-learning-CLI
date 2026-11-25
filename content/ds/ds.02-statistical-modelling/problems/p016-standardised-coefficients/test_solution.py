import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm

from solution import standardised_coefs


def make_df(seed, n=200):
    rng = np.random.default_rng(seed)
    hours = rng.normal(10, 2, n)
    age = rng.normal(40, 10, n)
    score = 5 + 3 * hours + 0.4 * age + rng.normal(0, 4, n)
    return pd.DataFrame({"hours": hours, "age": age, "score": score})


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_equals_b_times_sdx_over_sdy(seed):
    df = make_df(seed)
    raw = sm.OLS(df["score"], sm.add_constant(df[["hours", "age"]])).fit().params
    out = standardised_coefs(df, "score", ["hours", "age"])
    for name in ["hours", "age"]:
        expected = raw[name] * df[name].std() / df["score"].std()
        assert out[name] == pytest.approx(expected, rel=1e-8), f"{name}: should equal b * sd(x) / sd(y). Standardise the response as well, with the same ddof."


def test_result_is_a_series_without_intercept():
    out = standardised_coefs(make_df(0), "score", ["hours", "age"])
    assert isinstance(out, pd.Series), "return a pandas Series indexed by predictor name."
    assert list(out.index) == ["hours", "age"], "index must be the predictors in the given order, without 'const'."


def test_units_do_not_matter():
    df = make_df(3)
    df2 = df.assign(hours=df["hours"] * 60)         # hours -> minutes
    a = standardised_coefs(df, "score", ["hours", "age"])
    b = standardised_coefs(df2, "score", ["hours", "age"])
    assert b["hours"] == pytest.approx(a["hours"], rel=1e-8), "changing the unit of x must not change its standardised coefficient."


def test_input_is_not_modified():
    df = make_df(4)
    before = df.copy()
    standardised_coefs(df, "score", ["hours", "age"])
    pd.testing.assert_frame_equal(df, before)
