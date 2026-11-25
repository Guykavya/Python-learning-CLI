import pandas as pd

from solution import combine_months


def test_example():
    jan = pd.Series([5, 3], index=["tea", "milk"])
    feb = pd.Series([4, 2], index=["milk", "rice"])
    out = combine_months(jan, feb)
    assert out.to_dict() == {"milk": 7, "rice": 2, "tea": 5}, (
        "products found in only one month must count as 0 for the other: a.add(b, fill_value=0). Got %s." % out.to_dict())
    assert out.index.tolist() == ["milk", "rice", "tea"], "the result must be sorted by label: .sort_index()."


def test_dtype_is_integer_and_no_missing():
    jan = pd.Series([1, 2, 3], index=["a", "b", "c"])
    feb = pd.Series([10, 20, 30], index=["c", "d", "e"])
    out = combine_months(jan, feb)
    assert str(out.dtype) == "int64", "dtype is %s; the missing labels made floats. Convert back with .astype('int64')." % out.dtype
    assert not out.isna().any(), "NaN left in the result: use fill_value=0 so a missing month counts as 0."
    assert out.to_dict() == {"a": 1, "b": 2, "c": 13, "d": 20, "e": 30}, "c is in both months (3 + 10), the others in one."


def test_same_labels_in_different_order():
    jan = pd.Series([1, 2, 3], index=["z", "y", "x"])
    feb = pd.Series([10, 20, 30], index=["x", "y", "z"])
    out = combine_months(jan, feb)
    assert out.to_dict() == {"x": 13, "y": 22, "z": 31}, "alignment matches labels, not positions: z is 1 + 30."
    assert out.index.tolist() == ["x", "y", "z"], "sorted by label."


def test_no_common_labels_and_empty():
    out = combine_months(pd.Series([1], index=["a"]), pd.Series([2], index=["b"]))
    assert out.to_dict() == {"a": 1, "b": 2}
    empty = pd.Series([], dtype="int64")
    out = combine_months(empty, pd.Series([4], index=["q"]))
    assert out.to_dict() == {"q": 4} and str(out.dtype) == "int64", "an empty month adds nothing; dtype stays int64."


def test_inputs_not_changed():
    jan = pd.Series([5, 3], index=["tea", "milk"])
    feb = pd.Series([4, 2], index=["milk", "rice"])
    j0, f0 = jan.copy(), feb.copy()
    combine_months(jan, feb)
    pd.testing.assert_series_equal(jan, j0, obj="january")
    pd.testing.assert_series_equal(feb, f0, obj="february")
