import pandas as pd
import pytest

from solution import normalise_keys


def sku_left():
    return pd.DataFrame({"sku": ["P001", " p002", "P003 ", "P004", "p001"], "qty": [1, 2, 3, 4, 5]})


def sku_right():
    return pd.DataFrame({"sku": ["p001", "P002", "P003", "P005"], "name": ["tea", "milk", "rice", "salt"]})


def id_left():
    return pd.DataFrame({"order_id": [10001, 10002, 10003, 10004], "amount": [5.0, 6.0, 7.0, 8.0]})


def id_right():
    return pd.DataFrame({"order_id": ["10001", " 10002", "10004 ", "10009"], "status": ["paid"] * 4})


def test_returns_all_parts():
    r = normalise_keys(sku_left(), sku_right(), "sku")
    assert set(r) == {"left", "right", "match_before", "match_after", "unmatched"}, "return a dict with the five keys."


def test_keys_cleaned_on_both_sides():
    r = normalise_keys(sku_left(), sku_right(), "sku")
    assert r["left"]["sku"].tolist() == ["P001", "P002", "P003", "P004", "P001"], (
        "left keys: strip the spaces at both ends and upper-case: .str.strip().str.upper(). Got %s." % r["left"]["sku"].tolist())
    assert r["right"]["sku"].tolist() == ["P001", "P002", "P003", "P005"], "clean the right keys the same way."
    assert r["left"]["qty"].tolist() == [1, 2, 3, 4, 5] and r["right"]["name"].tolist()[0] == "tea", (
        "only the key column changes; other columns stay as they were.")


def test_match_rates_text_keys():
    r = normalise_keys(sku_left(), sku_right(), "sku")
    assert type(r["match_before"]) is float and type(r["match_after"]) is float, "match rates must be plain floats."
    assert r["match_before"] == pytest.approx(0.2), (
        "before cleaning only 'p001' (the 5th left row) matches exactly: 1 of 5 rows = 0.2. Got %s." % r["match_before"])
    assert r["match_after"] == pytest.approx(0.8), (
        "after cleaning 4 of 5 left ROWS match (P001 twice, P002, P003): 0.8. Count rows, not distinct keys. "
        "Got %s." % r["match_after"])
    assert r["unmatched"] == ["P004"], "P004 is still not in the right table. Got %s." % (r["unmatched"],)


def test_integer_against_text_ids():
    r = normalise_keys(id_left(), id_right(), "order_id")
    assert r["match_before"] == pytest.approx(0.0), (
        "the integer 10001 is not equal to the text '10001': before cleaning nothing matches. Got %s." % r["match_before"])
    assert r["left"]["order_id"].tolist() == ["10001", "10002", "10003", "10004"], (
        "convert the key to text first (astype(str)), then strip and upper-case.")
    assert r["right"]["order_id"].tolist() == ["10001", "10002", "10004", "10009"]
    assert r["match_after"] == pytest.approx(0.75), "after cleaning 3 of 4 orders match."
    assert r["unmatched"] == ["10003"]


def test_cleaned_frames_now_merge():
    r = normalise_keys(id_left(), id_right(), "order_id")
    m = r["left"].merge(r["right"], on="order_id", how="left", validate="1:1")
    assert len(m) == 4 and m["status"].notna().sum() == 3, "after cleaning, the merge works and matches 3 rows."


def test_unmatched_sorted_and_unique():
    left = pd.DataFrame({"k": ["zz", "b", "ZZ ", "a", "x"]})
    right = pd.DataFrame({"k": ["X"]})
    r = normalise_keys(left, right, "k")
    assert r["unmatched"] == ["A", "B", "ZZ"], "each failing cleaned key once, sorted. Got %s." % (r["unmatched"],)


def test_inputs_not_changed():
    l, rt = sku_left(), sku_right()
    lb, rb = l.copy(), rt.copy()
    normalise_keys(l, rt, "sku")
    pd.testing.assert_frame_equal(l, lb, obj="the input left frame")
    pd.testing.assert_frame_equal(rt, rb, obj="the input right frame")
