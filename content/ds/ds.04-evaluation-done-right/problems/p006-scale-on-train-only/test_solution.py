import numpy as np
import pytest

from solution import scale_split


def data(seed=0):
    rng = np.random.default_rng(seed)
    X_train = rng.normal(50, 10, size=(200, 3))
    X_test = rng.normal(50, 10, size=(40, 3))
    X_test[0] = 1e6                      # a sentinel row: if it influences the scaler, everything shifts
    return X_train, X_test


def test_training_rows_have_mean_zero_and_sd_one():
    X_train, X_test = data()
    a, b = scale_split(X_train, X_test)
    assert np.allclose(a.mean(axis=0), 0, atol=1e-9) and np.allclose(a.std(axis=0), 1, atol=1e-9), "the training rows must be exactly standardised: the scaler is fitted on them only. Did the test rows (with a 1e6 sentinel) leak into the fit?"


def test_test_rows_use_the_training_mean_and_sd():
    X_train, X_test = data()
    _, b = scale_split(X_train, X_test)
    expected = (X_test - X_train.mean(axis=0)) / X_train.std(axis=0)
    assert np.allclose(b, expected), "the test rows must be transformed with the TRAINING mean and standard deviation, not their own."


def test_small_example():
    a, b = scale_split(np.array([[1.0], [2.0], [3.0]]), np.array([[1e6]]))
    assert a.ravel() == pytest.approx([-1.2247449, 0.0, 1.2247449]), "train scaled by its own mean 2 and sd 0.8165."
    assert b.ravel() == pytest.approx([(1e6 - 2) / np.sqrt(2 / 3)]), "the test value is only transformed."


def test_inputs_unchanged():
    X_train, X_test = data(1)
    a0, b0 = X_train.copy(), X_test.copy()
    scale_split(X_train, X_test)
    assert np.array_equal(X_train, a0) and np.array_equal(X_test, b0), "do not modify the inputs."
