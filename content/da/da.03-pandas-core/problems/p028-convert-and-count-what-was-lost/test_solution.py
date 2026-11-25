import math

import pandas as pd

from solution import convert_numbers


def test_example():
    s = pd.Series(["12", " 3.5 ", "abc", "", None, "1,000", "abc", "7"])
    numbers, bad = convert_numbers(s)
    want = [12.0, 3.5, None, None, None, None, None, 7.0]
    got = numbers.tolist()
    for g, w in zip(got, want):
        assert (w is None and math.isnan(g)) or g == w, "numbers differ: got %s." % got
    assert bad == ["1,000", "abc"], "bad_values must hold the non-empty texts that became NaN, sorted, each once; got %s." % bad


def test_dtype_and_index():
    s = pd.Series(["1", "2", "x"], index=[10, 20, 30])
    numbers, bad = convert_numbers(s)
    assert str(numbers.dtype) == "float64", "numbers dtype is %s, expected float64." % numbers.dtype
    assert numbers.index.tolist() == [10, 20, 30], "keep the index of the input."
    assert bad == ["x"]


def test_spaces_are_stripped_before_converting():
    numbers, bad = convert_numbers(pd.Series(["  5", "6  ", " 7 8 "]))
    assert numbers.tolist()[:2] == [5.0, 6.0], "'  5' and '6  ' are numbers once the spaces are stripped."
    assert bad == ["7 8"], "an inner space is not a number; it is reported stripped, got %s." % bad


def test_empty_text_and_blank_are_not_reported():
    numbers, bad = convert_numbers(pd.Series(["", "   ", None, "4"]))
    assert bad == [], "empty, blank and missing values had no value to lose; got %s." % bad
    assert numbers.isna().tolist() == [True, True, True, False]


def test_everything_ok_gives_empty_list():
    numbers, bad = convert_numbers(pd.Series(["1", "2.5", "-3", "1e3"]))
    assert numbers.tolist() == [1.0, 2.5, -3.0, 1000.0] and bad == []


def test_input_not_changed():
    s = pd.Series([" 1", "a", None])
    before = s.copy()
    convert_numbers(s)
    pd.testing.assert_series_equal(s, before, obj="the input Series")
