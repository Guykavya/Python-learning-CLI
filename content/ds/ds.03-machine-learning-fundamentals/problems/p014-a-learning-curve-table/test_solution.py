import numpy as np
import pandas as pd
import pytest

from conftest import make_curve, poly_model
from solution import learning_curve_table

SIZES = [12, 20, 40, 80, 160]


@pytest.fixture(scope="module")
def setup():
    pool_X, pool_y = make_curve(400, seed=7)
    val_X, val_y = make_curve(1000, seed=8)
    return pool_X, pool_y, val_X, val_y


def test_columns_and_rows(setup):
    out = learning_curve_table(lambda: poly_model(3), *setup[:2], SIZES, *setup[2:], repeats=6)
    assert list(out.columns) == ["n_train", "train_rmse", "val_rmse", "gap"], "columns: n_train, train_rmse, val_rmse, gap."
    assert out["n_train"].tolist() == SIZES, "one row per size, in the order given."
    assert np.allclose(out["gap"], out["val_rmse"] - out["train_rmse"]), "gap = val_rmse - train_rmse."


def test_the_shape_of_a_good_model(setup):
    out = learning_curve_table(lambda: poly_model(3), *setup[:2], SIZES, *setup[2:], repeats=10)
    assert out["train_rmse"].iloc[-1] > out["train_rmse"].iloc[0], "training error rises with n: more rows are harder to fit exactly."
    assert out["val_rmse"].iloc[-1] < out["val_rmse"].iloc[0], "validation error falls with n."
    assert out["gap"].iloc[-1] < out["gap"].iloc[0] and out["gap"].iloc[-1] < 0.05, "the gap closes as the training set grows."


def test_exact_values_with_the_stated_sampling(setup):
    pool_X, pool_y, val_X, val_y = setup
    out = learning_curve_table(lambda: poly_model(2), pool_X, pool_y, [20, 50], val_X, val_y, repeats=4, seed=3)
    rng = np.random.default_rng(3)
    exp = []
    for n in [20, 50]:
        tr, va = [], []
        for _ in range(4):
            idx = rng.choice(len(pool_X), n, replace=False)
            m = poly_model(2).fit(pool_X[idx], pool_y[idx])
            tr.append(np.sqrt(np.mean((pool_y[idx] - m.predict(pool_X[idx])) ** 2)))
            va.append(np.sqrt(np.mean((val_y - m.predict(val_X)) ** 2)))
        exp.append((np.mean(tr), np.mean(va)))
    assert out["train_rmse"].to_numpy() == pytest.approx([e[0] for e in exp], rel=1e-9), "train_rmse is the mean over repeats of the RMSE on the rows the model was fitted on; use ONE default_rng(seed) and rng.choice(len(X), n, replace=False)."
    assert out["val_rmse"].to_numpy() == pytest.approx([e[1] for e in exp], rel=1e-9), "val_rmse is the mean RMSE on the fixed validation set."


def test_same_seed_same_table(setup):
    a = learning_curve_table(lambda: poly_model(1), *setup[:2], [20, 40], *setup[2:], repeats=3, seed=1)
    b = learning_curve_table(lambda: poly_model(1), *setup[:2], [20, 40], *setup[2:], repeats=3, seed=1)
    pd.testing.assert_frame_equal(a, b)
