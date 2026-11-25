import pandas as pd

from solution import revenue_by


def lines():
    return pd.DataFrame({
        "order_id": [10, 10, 11, 12, 12, 13, 14, 15],
        "product_id": ["P2", "P1", "P2", "P3", "P1", "P1", "P3", "P2"],
        "store_id": ["S2", "S2", "S1", "S3", "S3", "S1", "S2", "S1"],
        "channel": ["store", "store", "online", "store", "store", "store", "online", "online"],
        "revenue": [10.0, 4.0, 6.0, 30.0, 2.0, 8.0, 5.0, 1.0],
    })


def test_one_key_as_a_string():
    out = revenue_by(lines(), "store_id")
    want = pd.DataFrame({"store_id": ["S1", "S2", "S3"], "revenue": [15.0, 19.0, 32.0]})
    assert list(out.columns) == ["store_id", "revenue"], (
        "columns must be the key, then revenue. Got %s. Did you keep the key in the index? Use as_index=False "
        "or reset_index()." % list(out.columns))
    pd.testing.assert_frame_equal(out, want, check_dtype=False, obj="revenue by store_id")


def test_one_key_as_a_list():
    out = revenue_by(lines(), ["product_id"])
    want = pd.DataFrame({"product_id": ["P1", "P2", "P3"], "revenue": [14.0, 17.0, 35.0]})
    pd.testing.assert_frame_equal(out, want, check_dtype=False, obj="revenue by ['product_id']")


def test_two_keys_give_flat_columns():
    out = revenue_by(lines(), ["store_id", "channel"])
    assert not isinstance(out.index, pd.MultiIndex), (
        "two keys make a MultiIndex unless you use as_index=False or reset_index(): the keys must be columns.")
    assert list(out.columns) == ["store_id", "channel", "revenue"], "columns: the keys in the given order, then revenue."
    want = pd.DataFrame({
        "store_id": ["S1", "S1", "S2", "S2", "S3"],
        "channel": ["online", "store", "online", "store", "store"],
        "revenue": [7.0, 8.0, 5.0, 14.0, 32.0],
    })
    pd.testing.assert_frame_equal(out, want, check_dtype=False, obj="revenue by store and channel (sorted by both keys)")


def test_key_order_matters_for_sorting():
    out = revenue_by(lines(), ["channel", "store_id"])
    assert out["channel"].tolist() == ["online", "online", "store", "store", "store"], (
        "sort by the FIRST key first: all 'online' rows come before 'store'. Got %s." % out["channel"].tolist())
    assert out["store_id"].tolist() == ["S1", "S2", "S1", "S2", "S3"], "inside each channel, stores are sorted."
    assert out["revenue"].tolist() == [7.0, 5.0, 8.0, 14.0, 32.0]


def test_index_is_0_to_n_minus_1():
    out = revenue_by(lines(), ["store_id", "channel"])
    assert out.index.tolist() == list(range(len(out))), "the index must be 0, 1, 2, ... after flattening."


def test_total_is_kept():
    df = lines()
    for keys in ["store_id", ["store_id", "channel"], ["product_id", "store_id"]]:
        out = revenue_by(df, keys)
        assert abs(out["revenue"].sum() - df["revenue"].sum()) < 1e-9, (
            "the group totals must add up to the table total (%s): no row may be lost or counted twice." % (keys,))


def test_input_not_changed():
    df = lines()
    before = df.copy()
    revenue_by(df, ["store_id", "channel"])
    pd.testing.assert_frame_equal(df, before, obj="the input lines")
