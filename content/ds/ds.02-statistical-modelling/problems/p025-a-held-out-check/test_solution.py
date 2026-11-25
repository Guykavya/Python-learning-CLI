import numpy as np
import pandas as pd
import pytest
import statsmodels.formula.api as smf

from solution import holdout_rmse

JUNK = "y ~ x0 + " + " + ".join(f"j{i}" for i in range(20))


def make(n, seed, k=20):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, k + 1))
    df = pd.DataFrame(X, columns=["x0"] + [f"j{i}" for i in range(k)])
    df["y"] = 2 + 1.5 * df["x0"] + rng.normal(0, 2, n)
    return df


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_overfit_model_is_worse_on_new_data(seed):
    out = holdout_rmse(make(60, seed), JUNK, 0.25, seed)
    assert out["test_rmse"] > 1.15 * out["train_rmse"], f"train {out['train_rmse']:.2f}, test {out['test_rmse']:.2f}: 21 predictors for 45 rows must fit the training rows better than new rows. Evaluate on rows the model did NOT see."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_small_model_generalises_better_than_junk_model(seed):
    df = make(60, seed)
    small = holdout_rmse(df, "y ~ x0", 0.25, seed)
    junk = holdout_rmse(df, JUNK, 0.25, seed)
    assert small["test_rmse"] < junk["test_rmse"], "the model with only the real predictor should have the lower test error."
    assert small["test_rmse"] < 1.3 * small["train_rmse"], "a well-specified small model has train and test errors of similar size."


def test_exact_split_and_values():
    df = make(40, 4, k=2)
    out = holdout_rmse(df, "y ~ x0", 0.25, 9)
    idx = np.random.default_rng(9).permutation(40)
    train, test = df.iloc[idx[:30]], df.iloc[idx[30:]]
    res = smf.ols("y ~ x0", data=train).fit()
    exp_train = float(np.sqrt(np.mean((train["y"] - res.predict(train)) ** 2)))
    exp_test = float(np.sqrt(np.mean((test["y"] - res.predict(test)) ** 2)))
    assert out["train_rmse"] == pytest.approx(exp_train), "train_rmse: RMSE of the training rows (30 of 40)."
    assert out["test_rmse"] == pytest.approx(exp_test), "test_rmse: RMSE of the 10 held-out rows, using the model fitted on the 30 training rows."


def test_same_seed_same_result_different_seed_differs():
    df = make(60, 0)
    assert holdout_rmse(df, "y ~ x0", 0.25, 1) == holdout_rmse(df, "y ~ x0", 0.25, 1), "the split must be repeatable for a given seed."
    assert holdout_rmse(df, "y ~ x0", 0.25, 1) != holdout_rmse(df, "y ~ x0", 0.25, 2), "a different seed should give a different split."
