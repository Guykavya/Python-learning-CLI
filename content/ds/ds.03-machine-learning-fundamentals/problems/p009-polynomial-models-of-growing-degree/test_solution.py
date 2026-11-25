import pytest

from conftest import make_curve
from solution import fit_errors


@pytest.fixture(scope="module")
def data():
    X_tr, y_tr = make_curve(20, seed=1)
    X_val, y_val = make_curve(2000, seed=2)
    return X_tr, y_tr, X_val, y_val


def test_training_error_never_rises_with_degree(data):
    errs = [fit_errors(d, *data)[0] for d in range(0, 9)]
    for a, b in zip(errs, errs[1:]):
        assert b <= a * (1 + 1e-6) + 1e-9, f"training RMSE rose from {a:.4f} to {b:.4f}: a bigger polynomial can always fit the training rows at least as well."


def test_line_underfits_and_wiggles_overfit(data):
    t1, v1 = fit_errors(1, *data)
    t3, v3 = fit_errors(3, *data)
    t12, v12 = fit_errors(12, *data)
    assert t1 > 0.45 and v1 > 0.45, "a straight line cannot follow a sine: both errors stay about 0.5."
    assert v3 < 0.4, "degree 3 is about right: validation RMSE close to the noise level 0.3."
    assert t12 < t3 and v12 > 1.5 * v3, "degree 12 fits the 20 training rows better but does clearly worse on new rows. Evaluate on the validation rows."


def test_returns_two_floats(data):
    out = fit_errors(2, *data)
    assert len(out) == 2 and all(isinstance(v, float) for v in out), "return (train_rmse, val_rmse) as plain floats."


def test_validation_error_is_measured_on_the_validation_rows(data):
    X_tr, y_tr, X_val, y_val = data
    t, v = fit_errors(3, X_tr, y_tr, X_val, y_val)
    t2, v2 = fit_errors(3, X_tr, y_tr, X_tr, y_tr)
    assert v2 == pytest.approx(t), "evaluating on the training rows must give the training error."
    assert v != pytest.approx(t, rel=1e-6), "the validation error is computed on different rows from the training error."
