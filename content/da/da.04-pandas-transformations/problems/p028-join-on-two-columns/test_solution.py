import pandas as pd

from solution import daily_targets

D1, D2, D3 = pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-02"), pd.Timestamp("2025-01-03")


def sales():
    return pd.DataFrame({
        "store_id": ["S1", "S1", "S2", "S2", "S1"],
        "date": [D1, D2, D1, D2, D3],
        "revenue": [100.0, 80.0, 50.0, 70.0, 90.0],
    })


def targets():
    return pd.DataFrame({
        "store_id": ["S2", "S1", "S1", "S2", "S3"],
        "date": [D2, D1, D2, D1, D1],
        "target": [60.0, 90.0, 90.0, 60.0, 10.0],
    })


def result():
    return daily_targets(sales(), targets())


def test_row_count_is_the_sales_count():
    out = result()
    assert len(out) == 5, (
        "one row per sales row (5), got %d. Joining on store_id alone matches each sales day with EVERY target day of "
        "the store (S1: 3 x 2 = 6 rows): a many-to-many fan-out. Join on both columns: on=['store_id', 'date']."
        % len(out))


def test_columns_and_order():
    out = result()
    assert list(out.columns) == ["store_id", "date", "revenue", "target", "hit"], (
        "columns: store_id, date, revenue, target, hit. A date_x / date_y pair means date was not part of the key. "
        "Got %s." % list(out.columns))
    assert out["revenue"].tolist() == [100.0, 80.0, 50.0, 70.0, 90.0], "sales rows in the original order."
    assert out.index.tolist() == list(range(5)), "index 0..n-1."


def test_targets_matched_by_store_and_date():
    t = result()["target"].tolist()
    assert t[:4] == [90.0, 90.0, 60.0, 60.0], "each sales row gets the target of the same store on the same day. Got %s." % t
    assert pd.isna(t[4]), "S1 has no target on Jan 3: missing, not 0."


def test_hit():
    out = result()
    assert out["hit"].tolist() == [True, False, False, True, False], (
        "hit = revenue >= target: 100>=90 yes, 80>=90 no, 50>=60 no, 70>=60 yes; no target -> False. "
        "Got %s." % out["hit"].tolist())
    assert out["hit"].dtype == bool, "hit must be a bool column."


def test_targets_without_sales_ignored():
    assert "S3" not in set(result()["store_id"]), "S3 has a target but no sales: it is not a sales row."


def test_inputs_not_changed():
    s, t = sales(), targets()
    sb, tb = s.copy(), t.copy()
    daily_targets(s, t)
    pd.testing.assert_frame_equal(s, sb, obj="the input sales")
    pd.testing.assert_frame_equal(t, tb, obj="the input targets")
