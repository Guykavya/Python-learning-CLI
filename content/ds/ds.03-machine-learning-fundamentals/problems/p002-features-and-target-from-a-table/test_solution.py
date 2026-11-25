import pandas as pd
import pytest

from solution import split_xy


def make():
    return pd.DataFrame({"area": [50, 70, 90], "rooms": [2, 3, 4], "price": [10.0, 14.5, 20.0]})


def test_x_and_y():
    X, y = split_xy(make(), "price")
    assert list(X.columns) == ["area", "rooms"], "X must hold every column except the target, in the original order."
    assert isinstance(y, pd.Series) and y.tolist() == [10.0, 14.5, 20.0], "y must be the target column as a Series."


def test_original_is_unchanged():
    df = make()
    split_xy(df, "price")
    assert list(df.columns) == ["area", "rooms", "price"], "do not remove the target from the caller's DataFrame (pop/del change it)."


def test_changing_x_does_not_change_df():
    df = make()
    X, _ = split_xy(df, "price")
    X.loc[0, "area"] = -1
    assert df.loc[0, "area"] == 50, "X must be a new table: editing it must not edit df."


def test_target_in_the_middle():
    df = make()[["area", "price", "rooms"]]
    X, y = split_xy(df, "price")
    assert list(X.columns) == ["area", "rooms"] and y.name == "price", "the target can be any column."


def test_missing_target_message():
    with pytest.raises(KeyError) as e:
        split_xy(make(), "cost")
    msg = str(e.value)
    assert "cost" in msg and "area" in msg and "rooms" in msg and "price" in msg, "the error message must name the missing target and list the existing columns."
