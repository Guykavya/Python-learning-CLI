import pandas as pd
import pytest

from solution import to_money

CASES = [
    ("Rs. 1,250.50", 1250.5),
    ("₹980", 980.0),
    (" 12,000 ", 12000.0),
    ("45.25", 45.25),
    ("INR 3,00,000", 300000.0),
    ("Rs.80", 80.0),
    ("rs. 10", 10.0),
    ("Rs 5", 5.0),
    ("₹ 1,200.00", 1200.0),
    ("-5", -5.0),
    ("1,23,456.5", 123456.5),
    ("0", 0.0),
    ("n/a", None),
    ("-", None),
    ("", None),
    ("free", None),
    (None, None),
]


@pytest.mark.parametrize("text,want", CASES, ids=[repr(c[0]) for c in CASES])
def test_each_case(text, want):
    got = to_money(pd.Series([text, "1"]))
    assert isinstance(got, pd.Series), f"return a Series, not a {type(got).__name__}."
    value = got.iloc[0]
    if want is None:
        assert pd.isna(value), (
            f"{text!r} is not a number, so it must become missing; got {value!r}. "
            "pd.to_numeric(errors='coerce') turns the leftovers into missing.")
    else:
        assert not pd.isna(value), (
            f"{text!r} should become {want}, got missing. Remove the currency mark and the commas, strip the spaces, "
            "and keep the minus sign in front of digits.")
        assert float(value) == pytest.approx(want), f"{text!r} should become {want}, got {value!r}."


def test_result_is_numeric_and_keeps_index_and_input():
    s = pd.Series(["₹1,000", "x", None], index=[7, 8, 9])
    before = s.tolist()
    got = to_money(s)
    assert got.index.tolist() == [7, 8, 9], "keep the original index."
    assert pd.api.types.is_numeric_dtype(got.dtype), f"the result must have a numeric dtype, got {got.dtype}."
    assert [None if pd.isna(v) else float(v) for v in got] == [1000.0, None, None], f"got {got.tolist()}."
    assert [None if pd.isna(v) else v for v in s] == [before[0], before[1], None], "do not modify the input Series."


def test_dash_as_a_missing_marker_is_not_zero():
    got = to_money(pd.Series(["-", "- ", "—"]))
    assert got.isna().all(), f"a dash on its own means 'no value': expected all missing, got {got.tolist()}."
