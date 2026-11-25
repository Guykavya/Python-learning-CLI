import pandas as pd
import pytest

from solution import clean_items, tap


def items():
    return pd.DataFrame({
        "order_id": [4, 1, 1, 2, 2, 3, 3, 4],
        "product_id": ["P4", "P1", "P2", "P1", "P3", "P2", "P2", "P1"],
        "qty": [1.0, 2.0, 1.0, None, 0.0, 3.0, 3.0, -1.0],
        "unit_price": [20.0, 10.0, 5.0, 10.0, 7.0, 5.0, 5.0, 10.0],
    })


def test_tap_records_and_returns_the_same_table():
    log = []
    d = items()
    back = tap(d, "x", log)
    assert back is d, "tap must return the very table it received (return d), or the chain breaks"
    assert log == [("x", (8, 4))], "tap appends (label, d.shape); got %s" % log


def test_log_story():
    log = []
    clean_items(items(), log)
    assert [label for label, _ in log] == ["start", "valid qty", "no duplicates", "with revenue", "per order"], (
        "tap after every step with exactly these labels, in order; got %s" % [label for label, _ in log])
    shapes = [shape for _, shape in log]
    assert shapes[0] == (8, 4), "start: the raw 8 x 4 table"
    assert shapes[1] == (5, 4), (
        "valid qty: drop the missing qty, the 0 and the -1 -> 5 rows; got %s (did you keep qty == 0 or negative?)" % (shapes[1],))
    assert shapes[2] == (4, 4), "no duplicates: order 3 lists P2 x3 twice -> 4 rows; got %s" % (shapes[2],)
    assert shapes[3] == (4, 5), "with revenue: one new column -> (4, 5); got %s" % (shapes[3],)
    assert shapes[4] == (3, 2), (
        "per order: orders 1, 3, 4 with columns order_id and revenue -> (3, 2); got %s (as_index=False?)" % (shapes[4],))


def test_result():
    out = clean_items(items(), [])
    assert list(out.columns) == ["order_id", "revenue"], "columns order_id and revenue; got %s" % list(out.columns)
    assert out["order_id"].tolist() == [1, 3, 4], "orders 1, 3, 4 sorted; order 2 has no valid line"
    assert out["revenue"].tolist() == pytest.approx([25.0, 15.0, 20.0]), (
        "order 1: 2x10 + 1x5 = 25; order 3: 3x5 once (the duplicate is dropped) = 15; order 4: 1x20 = 20")
    assert out.index.tolist() == [0, 1, 2], "fresh index"


def test_fresh_log_each_call():
    log = []
    clean_items(items(), log)
    clean_items(items(), log)
    assert len(log) == 10, "each call appends its own 5 records to the list it is given (do not use a global log)"


def test_input_unchanged():
    i = items()
    before = i.copy()
    clean_items(i, [])
    pd.testing.assert_frame_equal(i, before, obj="items")
