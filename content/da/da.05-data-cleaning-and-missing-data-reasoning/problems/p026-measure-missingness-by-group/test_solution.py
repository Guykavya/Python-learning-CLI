import numpy as np
import pandas as pd

from solution import missing_profile


def frame():
    return pd.DataFrame({
        "edu": [8, 8, 8, 12, 12, 16, 16, 16, 16],
        "income": [np.nan, 1, np.nan, 2, np.nan, 3, 4, 5, 6],
        "other": list("abcdefghi"),
    })


def test_worked_example():
    out = missing_profile(frame(), "edu", "income")
    assert list(out.columns) == ["edu", "rows", "missing", "rate"], (
        "columns must be the key, rows, missing, rate. Got %s." % list(out.columns))
    assert out["edu"].tolist() == [8, 12, 16], "sorted by rate, largest first: 2/3, then 1/2, then 0. Got %s." % out["edu"].tolist()
    assert out["rows"].tolist() == [3, 2, 4]
    assert out["missing"].tolist() == [2, 1, 0], "a group with no missing value stays in the table with missing = 0."
    assert np.allclose(out["rate"], [2 / 3, 0.5, 0.0]), "rate = missing / rows (a share from 0 to 1, not a percentage)."


def test_index_is_fresh_and_counts_are_integers():
    out = missing_profile(frame(), "edu", "income")
    assert out.index.tolist() == [0, 1, 2], "the index must be 0, 1, 2, ... after sorting."
    assert out["rows"].dtype.kind == "i" and out["missing"].dtype.kind == "i", "rows and missing are integer columns."


def test_ties_are_ordered_by_the_key():
    df = pd.DataFrame({"g": ["b", "b", "a", "a", "c", "c"], "x": [np.nan, 1, np.nan, 1, 1, 2]})
    out = missing_profile(df, "g", "x")
    assert out["g"].tolist() == ["a", "b", "c"], (
        "a and b both have rate 0.5: ties are ordered by the key, smallest first. Got %s." % out["g"].tolist())


def test_text_keys_and_missing_keys():
    df = pd.DataFrame({"g": ["x", "x", None, "y"], "v": [np.nan, 1.0, np.nan, 2.0]})
    out = missing_profile(df, "g", "v")
    assert out["g"].tolist() == ["x", "y"], "rows whose group key is missing are ignored (groupby drops them)."
    assert out["rows"].tolist() == [2, 1]


def test_all_missing_and_none_missing():
    df = pd.DataFrame({"g": [1, 1, 2, 2], "v": [np.nan, np.nan, 5.0, 6.0]})
    out = missing_profile(df, "g", "v")
    assert out["rate"].tolist() == [1.0, 0.0], "an all-missing group has rate 1.0, a complete group has rate 0.0."


def test_input_not_changed():
    df = frame()
    before = df.copy()
    missing_profile(df, "edu", "income")
    pd.testing.assert_frame_equal(df, before, obj="the input frame (do not add helper columns to it)")
