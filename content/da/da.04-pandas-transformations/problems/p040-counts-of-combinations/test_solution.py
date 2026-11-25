import pandas as pd
import pytest

from solution import channel_by_region


def orders():
    return pd.DataFrame({
        "order_id": range(1, 11),
        "store_id": ["S2", "S2", "S3", "S1", "S1", "S5", "S1", "S2", "S5", "S6"],
        "region": ["north", "north", "north", "west", "west", "south", "west", "north", "south", "west"],
        "channel": ["store", "store", "online", "online", "online", "store", "store", "store", "store", "online"],
    })


def test_labels():
    counts, shares = channel_by_region(orders())
    assert counts.index.tolist() == ["north", "south", "west"], "one row per region, sorted"
    assert counts.columns.tolist() == ["online", "store"], "one column per channel, sorted"
    assert shares.index.tolist() == counts.index.tolist() and shares.columns.tolist() == counts.columns.tolist(), (
        "shares has the same rows and columns as counts")


def test_counts():
    counts, _ = channel_by_region(orders())
    assert counts.loc["north"].tolist() == [1, 3], "north has 1 online and 3 store orders"
    assert counts.loc["west"].tolist() == [3, 1], "west has 3 online and 1 store order"
    assert counts.loc["south", "online"] == 0, "south has no online order: the count is 0, not missing"
    assert int(counts.to_numpy().sum()) == 10, "the counts must add up to the 10 orders"


def test_shares_rows_sum_to_one():
    _, shares = channel_by_region(orders())
    sums = shares.sum(axis=1).tolist()
    assert sums == pytest.approx([1.0, 1.0, 1.0]), (
        "each ROW must sum to 1 (normalize='index'); got row sums %s - normalize='columns' or True answer other questions" % sums)
    assert shares.loc["north"].tolist() == pytest.approx([0.25, 0.75]), "north: 1 of 4 orders online"
    assert shares.loc["south"].tolist() == pytest.approx([0.0, 1.0]), "south: all orders in store"


def test_input_unchanged():
    o = orders()
    before = o.copy()
    channel_by_region(o)
    pd.testing.assert_frame_equal(o, before, obj="orders")
