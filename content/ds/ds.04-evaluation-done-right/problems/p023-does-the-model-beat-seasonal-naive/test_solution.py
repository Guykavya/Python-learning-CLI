import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression

from conftest import make_sales
from solution import beats_seasonal_naive

ORIGINS = [400, 450, 500, 550, 600, 650]


def feats(d):
    dow = pd.get_dummies(d["dow"].astype("category").cat.set_categories(range(7)), prefix="dow", dtype=float)
    return pd.concat([d[["day", "promo"]], dow], axis=1)


def linear_model(train, future):
    return LinearRegression().fit(feats(train), train["sales"]).predict(feats(future))


def mean_model(train, future):
    return np.full(len(future), train["sales"].mean())


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_a_real_model_beats_the_baseline(seed):
    m, n, beats = beats_seasonal_naive(linear_model, make_sales(seed=seed), ORIGINS)
    assert beats is True and m < 0.75 * n, f"the linear model (MAE {m:.1f}) knows trend, weekday and the promo calendar; it must beat seasonal naive ({n:.1f}) clearly."


def test_the_mean_does_not():
    m, n, beats = beats_seasonal_naive(mean_model, make_sales(seed=0), ORIGINS)
    assert beats is False and m > n, "the overall mean ignores trend and season: it loses to seasonal naive."


def test_the_model_never_sees_future_sales():
    seen = []

    def spy(train, future):
        seen.append((len(train), list(future.columns)))
        return np.zeros(len(future))

    beats_seasonal_naive(spy, make_sales(seed=0), [100, 200], horizon=14)
    assert [s[0] for s in seen] == [100, 200], "train = df.iloc[:origin]."
    assert all("sales" not in cols for _, cols in seen), "pass the future rows WITHOUT the sales column."


def test_naive_error_value():
    df = make_sales(seed=1)
    _, n, _ = beats_seasonal_naive(mean_model, df, [500], horizon=14)
    s = df["sales"].to_numpy()
    expected = np.mean(np.abs(s[500:514] - np.array([s[493 + (i % 7)] for i in range(14)])))
    assert n == pytest.approx(expected), "the baseline repeats the last 7 training values."
