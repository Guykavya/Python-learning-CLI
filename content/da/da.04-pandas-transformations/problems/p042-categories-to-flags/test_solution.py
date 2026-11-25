import pandas as pd

from solution import channel_flags


def orders():
    return pd.DataFrame({
        "order_id": [10001, 10002, 10003, 10004, 10005, 10006],
        "customer_id": ["C01", "C02", "C01", "C03", "C04", "C02"],
        "store_id": ["S1", "S2", "S2", "S1", "S3", "S1"],
        "channel": ["store", "online", "store", "app", "online", "store"],
    })


def test_columns():
    out = channel_flags(orders())
    assert list(out.columns) == ["order_id", "customer_id", "store_id", "ch_app", "ch_online", "ch_store"], (
        "keep the other columns (unencoded!), drop channel, add ch_<value> columns in alphabetical order; got %s" % list(out.columns))


def test_flags_are_integers():
    out = channel_flags(orders())
    for c in ["ch_app", "ch_online", "ch_store"]:
        assert str(out[c].dtype) in ("int64", "int32"), "%s must hold integers 0/1 (dtype=int), not %s" % (c, out[c].dtype)


def test_flag_values():
    out = channel_flags(orders())
    assert out["ch_store"].tolist() == [1, 0, 1, 0, 0, 1], "ch_store is 1 exactly on the store orders"
    assert out["ch_app"].tolist() == [0, 0, 0, 1, 0, 0], "a third channel (app) needs its own column too"
    sums = out[["ch_app", "ch_online", "ch_store"]].sum(axis=1).tolist()
    assert sums == [1] * 6, "each row has exactly one channel, so its flags sum to 1; got %s" % sums


def test_other_columns_unchanged():
    out = channel_flags(orders())
    pd.testing.assert_frame_equal(out[["order_id", "customer_id", "store_id"]], orders()[["order_id", "customer_id", "store_id"]],
                                  obj="the other columns (must not be encoded or reordered)")


def test_input_unchanged():
    o = orders()
    before = o.copy()
    channel_flags(o)
    pd.testing.assert_frame_equal(o, before, obj="orders")
