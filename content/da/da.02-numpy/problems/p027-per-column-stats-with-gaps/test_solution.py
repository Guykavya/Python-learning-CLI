import warnings

import numpy as np
import pytest

from solution import column_stats


def call_strict(x):
    """Run column_stats with every warning turned into an error."""
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        return column_stats(x)


def check_shapes(s, cols):
    assert isinstance(s, dict), f"return a dict, not a {type(s).__name__}."
    assert set(s) == {"count", "mean", "std"}, f"the dict needs exactly the keys count, mean, std; got {sorted(s)}."
    for key in ("count", "mean", "std"):
        got = np.asarray(s[key])
        assert got.shape == (cols,), f"{key!r} needs one value per column, shape ({cols},); got {got.shape}. Did you aggregate over axis=1?"
    assert np.issubdtype(np.asarray(s["count"]).dtype, np.integer), f"count must be an integer array, got {np.asarray(s['count']).dtype}."
    assert np.asarray(s["mean"]).dtype == np.float64, f"mean must be float64, got {np.asarray(s['mean']).dtype}."
    assert np.asarray(s["std"]).dtype == np.float64, f"std must be float64, got {np.asarray(s['std']).dtype}."


def test_the_example():
    x = np.array([[1.0, np.nan, np.nan], [3.0, 4.0, np.nan], [5.0, 8.0, np.nan]])
    s = call_strict(x)
    check_shapes(s, 3)
    np.testing.assert_array_equal(s["count"], [3, 2, 0], err_msg="count = number of non-nan values per column (~np.isnan(x)).sum(axis=0).")
    np.testing.assert_allclose(s["mean"], [3.0, 6.0, np.nan], rtol=1e-12, err_msg="mean of the non-nan values per column; nan for an empty column.")
    np.testing.assert_allclose(s["std"], [np.std([1.0, 3.0, 5.0]), 2.0, np.nan], rtol=1e-12,
                               err_msg="std is the POPULATION std (ddof=0) of the non-nan values; nan for an empty column.")


def test_all_nan_column_gives_no_warning():
    x = np.array([[np.nan, 2.0], [np.nan, 4.0]])
    try:
        s = call_strict(x)
    except RuntimeWarning as w:
        pytest.fail(f"a RuntimeWarning was raised ({w}). np.nanmean / np.nanstd warn on an all-nan column: "
                    "divide with np.divide(..., where=count > 0) or handle empty columns yourself.")
    assert int(s["count"][0]) == 0, "the all-nan column has count 0."
    assert np.isnan(s["mean"][0]) and np.isnan(s["std"][0]), "an all-nan column has mean nan and std nan (not 0)."
    assert s["mean"][1] == 3.0 and s["std"][1] == 1.0, "column [2, 4]: mean 3, population std 1."


def test_zero_rows():
    x = np.empty((0, 4))
    try:
        s = call_strict(x)
    except RuntimeWarning as w:
        pytest.fail(f"zero rows raised a RuntimeWarning ({w}): every column is empty, so every mean is nan without a warning.")
    check_shapes(s, 4)
    np.testing.assert_array_equal(s["count"], [0, 0, 0, 0], err_msg="zero rows: every count is 0.")
    assert np.isnan(s["mean"]).all() and np.isnan(s["std"]).all(), "zero rows: every mean and std is nan."


def test_integer_table():
    x = np.array([[1, 10], [2, 20], [3, 60]])
    s = call_strict(x)
    check_shapes(s, 2)
    np.testing.assert_array_equal(s["count"], [3, 3], err_msg="an integer table has no nan: count = number of rows.")
    np.testing.assert_allclose(s["mean"], x.mean(axis=0), rtol=1e-12, err_msg="integer table: mean should equal x.mean(axis=0).")
    np.testing.assert_allclose(s["std"], x.std(axis=0), rtol=1e-12, err_msg="integer table: std should equal x.std(axis=0) (ddof=0).")


def test_single_value_column_has_std_zero():
    x = np.array([[7.0, 1.0], [np.nan, 2.0]])
    s = call_strict(x)
    assert s["std"][0] == 0.0, "a column with one value has population std 0 (ddof=0), not nan."


def test_input_is_not_changed():
    x = np.array([[1.0, np.nan], [np.nan, 4.0], [3.0, 5.0]])
    keep = x.copy()
    call_strict(x)
    np.testing.assert_array_equal(x, keep, err_msg="do not change the caller's array (for example x[np.isnan(x)] = 0).")


def test_random_tables_match_nanmean_and_nanstd():
    rng = np.random.default_rng(27)
    for _ in range(20):
        rows, cols = int(rng.integers(1, 40)), int(rng.integers(1, 6))
        x = rng.normal(50, 10, size=(rows, cols))
        x[rng.random((rows, cols)) < 0.3] = np.nan
        s = call_strict(x)
        check_shapes(s, cols)
        ok = (~np.isnan(x)).sum(axis=0) > 0
        np.testing.assert_array_equal(s["count"], (~np.isnan(x)).sum(axis=0), err_msg="count per column is wrong.")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            want_mean = np.nanmean(x, axis=0)
            want_std = np.nanstd(x, axis=0)
        np.testing.assert_allclose(s["mean"][ok], want_mean[ok], rtol=1e-12, err_msg="mean differs from np.nanmean.")
        np.testing.assert_allclose(s["std"][ok], want_std[ok], rtol=1e-9, err_msg="std differs from np.nanstd (ddof=0).")
        assert np.isnan(s["mean"][~ok]).all(), "columns without data must have mean nan."
