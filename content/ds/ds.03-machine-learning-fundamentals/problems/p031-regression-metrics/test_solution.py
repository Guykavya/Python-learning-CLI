import math

import numpy as np
import pytest
from sklearn import metrics

from solution import reg_metrics


def test_worked_example():
    out = reg_metrics([3, 5, 8], [2, 5, 10])
    assert out["MAE"] == pytest.approx(1.0), "MAE = (1 + 0 + 2) / 3 = 1."
    assert out["RMSE"] == pytest.approx(math.sqrt(5 / 3)), "RMSE = sqrt((1 + 0 + 4) / 3)."
    assert out["R2"] == pytest.approx(1 - 5 / ((3 - 16 / 3) ** 2 + (5 - 16 / 3) ** 2 + (8 - 16 / 3) ** 2)), "R2 = 1 - RSS / TSS with TSS around the mean of y (16/3)."
    assert out["MAPE"] == pytest.approx((1 / 3 + 0 + 2 / 8) / 3), "MAPE = mean(|e| / y)."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_matches_sklearn(seed):
    rng = np.random.default_rng(seed)
    y = rng.uniform(1, 10, 50)
    p = y + rng.normal(0, 1, 50)
    out = reg_metrics(y, p)
    assert out["MAE"] == pytest.approx(metrics.mean_absolute_error(y, p), rel=1e-10), "MAE differs from sklearn."
    assert out["RMSE"] == pytest.approx(math.sqrt(metrics.mean_squared_error(y, p)), rel=1e-10), "RMSE differs from sklearn (square root of the MSE)."
    assert out["R2"] == pytest.approx(metrics.r2_score(y, p), rel=1e-10), "R2 differs: the total sum of squares is around the MEAN of y."
    assert out["MAPE"] == pytest.approx(metrics.mean_absolute_percentage_error(y, p), rel=1e-10), "MAPE differs: divide the error by the true value y."


def test_a_perfect_and_a_mean_prediction():
    y = np.array([2.0, 4.0, 6.0, 8.0])
    assert reg_metrics(y, y)["R2"] == pytest.approx(1.0), "perfect predictions: R2 = 1."
    assert reg_metrics(y, np.full(4, y.mean()))["R2"] == pytest.approx(0.0, abs=1e-12), "predicting the mean: R2 = 0."
    assert reg_metrics(y, -y)["R2"] < 0, "predictions worse than the mean give a negative R2."


def test_errors():
    with pytest.raises(ValueError, match="MAPE"):
        reg_metrics([0.0, 1.0, 2.0], [1.0, 1.0, 1.0])
    with pytest.raises(ValueError, match="R2"):
        reg_metrics([3.0, 3.0, 3.0], [1.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        reg_metrics([1.0, 2.0], [1.0])


def test_plain_floats():
    out = reg_metrics([1.0, 2.0, 3.0], [1.1, 2.2, 2.9])
    assert all(type(v) is float for v in out.values()), "return plain floats."
