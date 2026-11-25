import numpy as np
import pytest

from solution import reliability


def test_worked_example():
    t = reliability([0, 0, 1, 1, 1], [0.05, 0.15, 0.12, 0.95, 0.91], 10)
    assert list(t.columns) == ["bin_low", "n", "predicted", "observed"], "columns: bin_low, n, predicted, observed."
    assert t["bin_low"].tolist() == pytest.approx([0.0, 0.1, 0.9]), "only the three non-empty bins, in order."
    assert t["n"].tolist() == [1, 2, 2], "rows per bin."
    assert t["predicted"].tolist() == pytest.approx([0.05, 0.135, 0.93]), "mean predicted probability per bin."
    assert t["observed"].tolist() == pytest.approx([0.0, 0.5, 1.0]), "observed rate per bin."


def test_probability_one_goes_to_the_last_bin():
    t = reliability([1, 0], [1.0, 0.95], 10)
    assert len(t) == 1 and t["n"].iloc[0] == 2 and t["bin_low"].iloc[0] == pytest.approx(0.9), "p = 1.0 belongs to the last bin [0.9, 1.0]."


def test_calibrated_simulation_lies_on_the_diagonal():
    rng = np.random.default_rng(0)
    p = rng.random(50000)
    y = (rng.random(50000) < p).astype(int)
    t = reliability(y, p, 10)
    assert len(t) == 10 and t["n"].sum() == 50000, "every row in exactly one bin."
    assert np.allclose(t["observed"], t["predicted"], atol=0.02), "for calibrated probabilities observed matches predicted in every bin."
