import numpy as np
import pandas as pd
import pytest

from solution import fill_gaps

NAN = np.nan


def make():
    return pd.Series([1.0, NAN, NAN, 4.0, NAN], index=list("abcde"), name="temp")


def check(got, want, index, what):
    assert isinstance(got, pd.Series), f"{what}: return a Series, not a {type(got).__name__}."
    assert got.index.tolist() == index, f"{what}: labels should be {index}, got {got.index.tolist()}. Do not reset the index."
    assert np.allclose(got.to_numpy(dtype=float), np.array(want, dtype=float), equal_nan=True), (
        f"{what}: expected {want}, got {got.tolist()}.")


def test_drop_keeps_labels():
    check(fill_gaps(make(), "drop"), [1.0, 4.0], ["a", "d"], "drop")


def test_zero():
    check(fill_gaps(make(), "zero"), [1, 0, 0, 4, 0], list("abcde"), "zero")


def test_ffill_copies_the_last_known_value():
    check(fill_gaps(make(), "ffill"), [1, 1, 1, 4, 4], list("abcde"), "ffill")


def test_ffill_leading_gap_stays_missing():
    s = pd.Series([NAN, 2.0, NAN])
    check(fill_gaps(s, "ffill"), [NAN, 2.0, 2.0], [0, 1, 2], "ffill with a leading gap")


def test_interpolate_draws_a_line():
    check(fill_gaps(make(), "interpolate"), [1, 2, 3, 4, 4], list("abcde"), "interpolate")


def test_interpolate_leading_gap_stays_missing():
    s = pd.Series([NAN, 1.0, NAN, 3.0])
    check(fill_gaps(s, "interpolate"), [NAN, 1.0, 2.0, 3.0], [0, 1, 2, 3], "interpolate with a leading gap")


def test_median_of_the_known_values():
    check(fill_gaps(make(), "median"), [1, 2.5, 2.5, 4, 2.5], list("abcde"), "median")
    s = pd.Series([1.0, NAN, 9.0, 100.0])
    check(fill_gaps(s, "median"), [1, 9, 9, 100], [0, 1, 2, 3], "median of 1, 9, 100 is 9 (not the mean, and not 0)")


def test_series_without_gaps_is_returned_equal():
    s = pd.Series([3.0, 1.0, 2.0])
    for how in ["drop", "zero", "ffill", "interpolate", "median"]:
        check(fill_gaps(s, how), [3.0, 1.0, 2.0], [0, 1, 2], f"no gaps, how={how!r}")


def test_unknown_word_raises_value_error():
    with pytest.raises(ValueError, match="bfill"):
        fill_gaps(make(), "bfill")


def test_input_is_not_changed():
    s = make()
    for how in ["drop", "zero", "ffill", "interpolate", "median"]:
        fill_gaps(s, how)
    assert s.isna().tolist() == [False, True, True, False, True], (
        "the input Series was modified: use fillna / ffill / dropna, which return new Series (no inplace=True).")
