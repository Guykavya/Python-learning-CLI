import pandas as pd
import pytest

from solution import index_by


def frame():
    return pd.DataFrame({"sku": ["A1", "B2", "C3", "D4"], "qty": [1, 2, 3, 4], "price": [9.5, 8.0, 7.0, 6.5]})


def test_unique_key_becomes_index():
    df = frame()
    out = index_by(df, "sku")
    assert out.index.tolist() == ["A1", "B2", "C3", "D4"], "the index must hold the sku values."
    assert out.index.name == "sku", "keep the index name: set_index('sku') names it."
    assert "sku" not in out.columns, "the key column moves into the index; it must leave the columns."
    assert out.loc["C3", "qty"] == 3


def test_duplicates_raise_and_name_every_duplicated_key():
    df = pd.DataFrame({"sku": ["A1", "B2", "A1", "C3", "B2", "A1"], "qty": [1, 2, 3, 4, 5, 6]})
    with pytest.raises(ValueError) as info:
        index_by(df, "sku")
    msg = str(info.value)
    assert "A1" in msg and "B2" in msg, "the message must list the duplicated keys A1 and B2, got: %r" % msg
    assert "C3" not in msg, "C3 appears once; only duplicated keys belong in the message."
    assert msg.count("A1") == 1, "list each duplicated key once (A1 appears three times in the data)."


def test_works_with_integer_keys():
    df = pd.DataFrame({"id": [10, 20, 10], "v": [1, 2, 3]})
    with pytest.raises(ValueError, match="10"):
        index_by(df, "id")
    ok = index_by(df.iloc[:2], "id")
    assert ok.loc[20, "v"] == 2


def test_missing_values_in_key_count_once_as_unique():
    df = pd.DataFrame({"k": ["a", "b", None], "v": [1, 2, 3]})
    out = index_by(df, "k")
    assert len(out) == 3, "one missing key is still unique; do not raise."


def test_input_not_changed():
    df = frame()
    before = df.copy()
    index_by(df, "sku")
    pd.testing.assert_frame_equal(df, before, obj="the input frame (set_index returns a new frame)")
    dup = pd.DataFrame({"sku": ["A", "A"], "qty": [1, 2]})
    before = dup.copy()
    with pytest.raises(ValueError):
        index_by(dup, "sku")
    pd.testing.assert_frame_equal(dup, before, obj="the input frame after the error")
