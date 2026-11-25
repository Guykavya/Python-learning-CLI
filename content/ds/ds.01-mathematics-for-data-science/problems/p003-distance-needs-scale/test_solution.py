import math

import numpy as np
import pytest

from solution import standardise, distances_from_first

X = np.array([[30, 50000.0], [31, 90000.0], [60, 51000.0], [33, 52000.0]])


def test_standardise_has_mean_zero_and_unit_std():
    Z = standardise(X)
    assert Z.mean(axis=0) == pytest.approx([0, 0], abs=1e-9), "every column must have mean 0 (subtract the column mean)."
    assert Z.std(axis=0) == pytest.approx([1, 1]), "every column must have std 1 (divide by the population std, axis=0)."


def test_standardise_does_not_change_the_input():
    before = X.copy()
    standardise(X)
    assert np.array_equal(X, before), "return a new array, do not modify X in place."


def test_constant_column_becomes_zero_not_nan():
    Z = standardise(np.array([[1.0, 5.0], [2.0, 5.0], [3.0, 5.0]]))
    assert not np.isnan(Z).any(), "a constant column has std 0: do not divide by 0."
    assert Z[:, 1] == pytest.approx([0, 0, 0]), "a constant column becomes all zeros."


def test_distances_from_first_shape_and_values():
    d = distances_from_first(np.array([[0.0, 0.0], [3.0, 4.0], [6.0, 8.0]]))
    assert d.shape == (2,), f"one distance per OTHER row: expected shape (2,), got {d.shape}."
    assert d == pytest.approx([5.0, 10.0]), "3-4-5 triangle, then twice as far."


def test_scaling_changes_the_nearest_person():
    raw = distances_from_first(X)
    scaled = distances_from_first(standardise(X))
    assert int(np.argmin(raw)) != int(np.argmin(scaled)), "on raw data income decides; after standardising the nearest person must change."
