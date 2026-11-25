import numpy as np
import pytest

from conftest import make_curve, poly_model
from solution import best_degree


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_the_sweet_spot_is_in_the_middle(seed):
    X_tr, y_tr = make_curve(100, seed=seed)
    X_val, y_val = make_curve(2000, seed=100 + seed)
    d = best_degree(X_tr, y_tr, X_val, y_val)
    assert 3 <= d <= 6, f"got degree {d}. A sine wave needs about degree 3-5; choose by VALIDATION error (lowest wins), not training error."


def test_matches_a_direct_scan():
    X_tr, y_tr = make_curve(60, seed=7)
    X_val, y_val = make_curve(1000, seed=8)
    errs = {}
    for d in range(1, 9):
        m = poly_model(d).fit(X_tr, y_tr)
        errs[d] = float(np.sqrt(np.mean((y_val - m.predict(X_val)) ** 2)))
    expected = min(errs, key=lambda d: (errs[d], d))
    assert best_degree(X_tr, y_tr, X_val, y_val, max_degree=8) == expected, "return the degree with the lowest validation RMSE among 1..max_degree."


def test_max_degree_is_respected():
    X_tr, y_tr = make_curve(100, seed=1)
    X_val, y_val = make_curve(500, seed=2)
    assert best_degree(X_tr, y_tr, X_val, y_val, max_degree=2) <= 2, "never return a degree above max_degree."


def test_training_error_would_choose_wrongly():
    X_tr, y_tr = make_curve(30, seed=1)
    X_val, y_val = make_curve(2000, seed=2)
    assert best_degree(X_tr, y_tr, X_val, y_val, max_degree=12) < 12, "the highest degree always has the lowest training error, but it must not be chosen by that."
