import math

import pandas as pd

from solution import parse_income

# (text, expected amount or None for missing)
CASES = [
    ("45000", 45000.0),
    ("₹45,000", 45000.0),
    ("Rs. 31000", 31000.0),
    ("rs 31,000", 31000.0),
    ("RS.12000", 12000.0),
    ("45k", 45000.0),
    ("4.5K", 4500.0),
    ("45000/-", 45000.0),
    ("  52000  ", 52000.0),
    ("12,34,567", 1234567.0),
    ("₹ 1,20,000/-", 120000.0),
    ("N/A", None),
    ("n/a", None),
    ("-999", None),
    ("", None),
    ("   ", None),
    ("forty", None),
    ("₹", None),
    ("-5000", None),
    ("4.5.6", None),
    ("k", None),
]


def one(text):
    out = parse_income(pd.Series([text]))
    return out.iloc[0]


def check(text, want):
    got = one(text)
    if want is None:
        assert pd.isna(got), "%r must become missing (NaN), but you returned %r." % (text, got)
    else:
        assert not pd.isna(got), "%r should be read as %s, but you returned NaN." % (text, want)
        assert math.isclose(float(got), want, rel_tol=1e-9), "%r should be %s, got %r." % (text, want, got)


def test_plain_numbers_and_currency_marks():
    for text, want in CASES[:5]:
        check(text, want)


def test_k_suffix_and_trailing_dash():
    for text, want in CASES[5:8]:
        check(text, want)


def test_spaces_and_indian_grouping_and_combined_decoration():
    for text, want in CASES[8:11]:
        check(text, want)


def test_codes_mean_missing():
    for text, want in CASES[11:16]:
        check(text, want)


def test_text_that_is_not_an_amount_is_missing_not_an_error():
    for text, want in CASES[16:]:
        check(text, want)


def test_missing_input_stays_missing():
    out = parse_income(pd.Series(["10", None, float("nan")]))
    assert out.iloc[0] == 10.0 and out.isna().tolist() == [False, True, True], (
        "a missing input gives a missing output. Got %s." % out.tolist())


def test_returns_float_series_with_same_index():
    s = pd.Series(["₹1,000", "x", "2k"], index=[7, 8, 9])
    out = parse_income(s)
    assert out.index.tolist() == [7, 8, 9], "keep the index of the input."
    assert str(out.dtype) == "float64", "return floats (so that missing values fit). Got dtype %s." % out.dtype
    assert out.tolist()[0] == 1000.0 and out.tolist()[2] == 2000.0 and math.isnan(out.tolist()[1])


def test_whole_column_and_input_unchanged():
    texts = [c[0] for c in CASES]
    s = pd.Series(texts)
    out = parse_income(s)
    assert s.tolist() == texts, "do not change the input Series."
    want = [float("nan") if c[1] is None else c[1] for c in CASES]
    for got, w in zip(out.tolist(), want):
        assert (math.isnan(got) and math.isnan(w)) or math.isclose(got, w, rel_tol=1e-9), (
            "whole-column result differs: got %s, expected %s." % (out.tolist(), want))
    assert int(out.isna().sum()) == sum(1 for c in CASES if c[1] is None)
