import numpy as np
import pandas as pd

from solution import to_missing


def frame():
    return pd.DataFrame({
        "city": ["Pune", " ", "n/a", "NA", "Delhi", None],
        "n": [1, 2, 3, 4, 5, 6],
        "note": ["ok", "-", "", "fine", "  - ", "x"],
    }, index=[5, 6, 7, 8, 9, 10])


def test_text_tokens_become_missing():
    clean, _ = to_missing(frame())
    assert clean["city"].isna().tolist() == [False, True, True, True, False, True], (
        "whitespace-only, 'n/a' and 'NA' must become real missing values. Got %s." % clean["city"].isna().tolist())
    assert clean["note"].isna().tolist() == [False, True, True, False, True, False], (
        "'-', '' and '  - ' (after strip) are tokens. Got %s." % clean["note"].isna().tolist())


def test_other_values_are_unchanged():
    clean, _ = to_missing(frame())
    assert clean["city"].dropna().tolist() == ["Pune", "Delhi"], "real words such as 'Pune' must stay exactly as they are."
    assert clean["note"].dropna().tolist() == ["ok", "fine", "x"]
    assert clean["n"].tolist() == [1, 2, 3, 4, 5, 6], "numeric columns are not touched."
    assert clean.index.tolist() == [5, 6, 7, 8, 9, 10], "keep the index."


def test_counts_skip_values_that_were_already_missing():
    _, counts = to_missing(frame())
    assert counts == {"city": 3, "n": 0, "note": 3}, (
        "counts must be {'city': 3, 'n': 0, 'note': 3}: the None in city was missing already. Got %s." % counts)
    assert all(type(v) is int for v in counts.values()), "counts are plain ints."


def test_case_is_ignored_and_custom_tokens():
    d = pd.DataFrame({"a": ["N/A", "na", "None", "x", "Unknown"]})
    clean, counts = to_missing(d, tokens=("n/a", "NA", "none", "unknown"))
    assert clean["a"].isna().tolist() == [True, True, True, False, True], (
        "token comparison ignores case: 'N/A', 'na', 'None', 'Unknown' all match. Got %s." % clean["a"].isna().tolist())
    assert counts == {"a": 4}


def test_default_tokens_do_not_catch_other_words():
    d = pd.DataFrame({"a": ["none", "unknown", "0", "NAN?"]})
    clean, counts = to_missing(d)
    assert clean["a"].isna().sum() == 0 and counts == {"a": 0}, "only the default tokens count; 'none' and 'unknown' are not default tokens."


def test_numeric_and_datetime_columns_are_skipped():
    d = pd.DataFrame({"x": [1.5, np.nan, 3.0], "when": pd.to_datetime(["2025-01-01", None, "2025-01-03"]), "t": ["-", "a", "b"]})
    clean, counts = to_missing(d)
    assert counts == {"x": 0, "when": 0, "t": 1}, "numeric and datetime columns count 0. Got %s." % counts
    assert clean["x"].isna().sum() == 1 and clean["when"].isna().sum() == 1, "their existing missing values stay."
    assert str(clean["x"].dtype) == "float64", "a numeric column must stay numeric."


def test_input_not_changed():
    d = frame()
    before = d.copy()
    to_missing(d)
    pd.testing.assert_frame_equal(d, before, obj="the input frame")
