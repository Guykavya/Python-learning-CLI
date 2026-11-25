import pandas as pd
import pytest

from solution import to_nullable_ints


def frame():
    return pd.DataFrame({
        "qty": [1.0, None, 3.0, 4.0],
        "stock": [10, 20, 30, 40],
        "price": [1.5, 2.5, 3.5, 4.5],
    }, index=[5, 6, 7, 8])


def test_float_with_gap_becomes_nullable_int():
    out = to_nullable_ints(frame(), ["qty"])
    assert str(out["qty"].dtype) == "Int64", "qty dtype is %s; the nullable integer dtype is 'Int64' (capital I)." % out["qty"].dtype
    assert out["qty"].isna().tolist() == [False, True, False, False], "the gap must stay missing."
    assert [None if pd.isna(v) else int(v) for v in out["qty"]] == [1, None, 3, 4]
    assert all(type(v) is int for v in out["qty"].dropna().tolist()), "the values should be whole numbers (1, not 1.0)."


def test_several_columns_and_plain_ints():
    out = to_nullable_ints(frame(), ["qty", "stock"])
    assert str(out["stock"].dtype) == "Int64", "an int64 column listed in cols also becomes Int64."
    assert out["stock"].tolist() == [10, 20, 30, 40]


def test_unlisted_columns_untouched():
    out = to_nullable_ints(frame(), ["qty"])
    assert str(out["price"].dtype) == "float64" and out["price"].tolist() == [1.5, 2.5, 3.5, 4.5]
    assert str(out["stock"].dtype) == "int64", "stock was not listed: it stays int64."
    assert out.index.tolist() == [5, 6, 7, 8]


def test_non_whole_number_raises_valueerror_naming_the_column():
    df = pd.DataFrame({"ok": [1.0, 2.0], "bad": [1.0, 2.5]})
    with pytest.raises(ValueError) as info:
        to_nullable_ints(df, ["ok", "bad"])
    assert "bad" in str(info.value), "the message must name the column: got %r." % str(info.value)


def test_non_whole_with_a_gap_also_raises():
    df = pd.DataFrame({"n": [None, 0.5, 2.0]})
    with pytest.raises(ValueError, match="n"):
        to_nullable_ints(df, ["n"])


def test_input_not_changed():
    df = frame()
    before = df.copy()
    to_nullable_ints(df, ["qty", "stock"])
    pd.testing.assert_frame_equal(df, before, obj="the input frame")


def test_empty_cols_list():
    df = frame()
    pd.testing.assert_frame_equal(to_nullable_ints(df, []), df, obj="nothing to convert")
