import numpy as np
import pandas as pd

from solution import age_bands, spend_quartiles


def band(age):
    if age is None or pd.isna(age) or age < 0:
        return None
    if age <= 18:
        return "youth"
    if age <= 40:
        return "adult"
    if age <= 65:
        return "middle"
    return "senior"


def plain(series):
    return [None if pd.isna(v) else str(v) for v in series]


def test_age_bands_boundaries():
    ages = pd.Series([0, 17, 18, 19, 40, 41, 65, 66, 120, -1, None])
    before = ages.copy()
    got = age_bands(ages)
    assert isinstance(got, pd.Series), f"return a Series, not a {type(got).__name__}."
    assert plain(got) == [band(a) for a in ages], (
        f"expected {[band(a) for a in ages]}, got {plain(got)}. Edges 0, 18, 40, 65, inf are right-closed: 18 is youth, "
        "40 is adult, 65 is middle; include_lowest=True puts 0 in youth; negative and missing ages have no label.")
    pd.testing.assert_series_equal(ages, before, obj="the input Series")


def test_age_bands_keep_the_index_and_work_on_floats():
    ages = pd.Series([18.0, 18.5, 64.9], index=[3, 2, 1])
    got = age_bands(ages)
    assert got.index.tolist() == [3, 2, 1], "keep the index of the input."
    assert plain(got) == ["youth", "adult", "middle"], f"18.0 is youth, 18.5 is adult, 64.9 is middle; got {plain(got)}."


def test_quartiles_boundary_values_go_to_the_lower_group():
    got = spend_quartiles(pd.Series([10, 20, 30, 40, 50]))
    assert plain(got) == ["Q1", "Q1", "Q2", "Q3", "Q4"], (
        f"the quartile edges are 10, 20, 30, 40, 50 and bins are right-closed: 20 is Q1, 30 is Q2, 40 is Q3. Got {plain(got)}.")


def test_quartiles_have_equal_counts():
    s = pd.Series(np.arange(1, 101)[::-1], index=np.arange(100) + 500)
    got = spend_quartiles(s)
    counts = got.value_counts()
    assert counts.sort_index().tolist() == [25, 25, 25, 25], f"100 values should give 25 per quartile, got {counts.sort_index().to_dict()}."
    assert plain(got)[0] == "Q4" and plain(got)[-1] == "Q1", "the largest value (first row, 100) is Q4 and the smallest (last row, 1) is Q1."
    assert got.index.tolist() == s.index.tolist(), "keep the index of the input."


def test_quartiles_missing_values_stay_missing():
    s = pd.Series([1.0, None, 2.0, 3.0, 4.0, None, 5.0, 6.0, 7.0, 8.0])
    got = spend_quartiles(s)
    assert got.isna().tolist() == s.isna().tolist(), "missing values stay missing, they are not a group."
    assert got.dropna().value_counts().sort_index().tolist() == [2, 2, 2, 2], f"8 known values: 2 per quartile; got {got.value_counts().sort_index().to_dict()}."


def test_equal_widths_differ_from_equal_counts():
    s = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 1000])
    q = spend_quartiles(s).value_counts().sort_index().tolist()
    w = pd.cut(s, 4).value_counts().sort_index().tolist()
    assert q == [3, 2, 2, 3] and w == [9, 0, 0, 1], "sanity check of the idea: qcut balances counts, cut balances widths."
