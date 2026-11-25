import pandas as pd
import pytest

from solution import apply_discount


def frame():
    return pd.DataFrame({
        "item": ["tea", "pen", "mug", "jam", "ink"],
        "category": ["food", "office", "home", "food", "office"],
        "price": [100.0, 20.0, 50.0, 80.0, 12.5],
        "qty": [1, 2, 3, 4, 5],
    }, index=[10, 11, 12, 13, 14])


def test_only_matching_rows_change():
    out = apply_discount(frame(), "food", 10)
    assert out["price"].tolist() == pytest.approx([90.0, 20.0, 50.0, 72.0, 12.5]), (
        "only the food rows (tea, jam) get 10%% off; got %s." % out["price"].tolist())


def test_input_frame_is_unchanged():
    df = frame()
    before = df.copy()
    apply_discount(df, "food", 10)
    pd.testing.assert_frame_equal(df, before, obj="the input frame: copy it first (df.copy()), then change the copy")


def test_returns_a_new_object():
    df = frame()
    out = apply_discount(df, "food", 10)
    assert out is not df, "return a new frame, not the input."


def test_other_columns_and_labels_unchanged():
    df = frame()
    out = apply_discount(df, "office", 50)
    assert out.index.tolist() == df.index.tolist() and out.columns.tolist() == df.columns.tolist()
    assert out["qty"].tolist() == df["qty"].tolist() and out["item"].tolist() == df["item"].tolist()
    assert out["price"].tolist() == pytest.approx([100.0, 10.0, 50.0, 80.0, 6.25])


def test_no_matching_category_changes_nothing():
    df = frame()
    out = apply_discount(df, "toys", 20)
    pd.testing.assert_frame_equal(out, df, obj="a category with no rows: nothing changes")


def test_zero_and_full_discount():
    df = frame()
    assert apply_discount(df, "home", 0)["price"].tolist() == df["price"].tolist()
    assert apply_discount(df, "home", 100)["price"].tolist()[2] == 0.0
