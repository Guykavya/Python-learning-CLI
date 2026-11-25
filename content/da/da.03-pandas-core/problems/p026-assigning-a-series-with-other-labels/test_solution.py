import math

import pandas as pd

from solution import attach_targets


def case():
    df = pd.DataFrame({"customer_id": [2, 0, 7, 2, 5, 1], "amount": [10, 20, 30, 40, 50, 60]})
    targets = pd.Series({0: 80, 1: 90, 2: 50, 5: 10})
    return df, targets


def plain(df, targets):
    lookup = dict(zip(targets.index.tolist(), targets.tolist()))
    return [lookup.get(c) for c in df["customer_id"].tolist()]


def same(got, want):
    assert len(got) == len(want)
    for g, w in zip(got, want):
        if w is None:
            assert pd.isna(g), "a customer without a target must give a missing value, got %r." % (g,)
        else:
            assert g == w, "wrong target: got %r, expected %r." % (g, w)


def test_example():
    df = pd.DataFrame({"customer_id": [2, 0, 7, 2]})
    out, n = attach_targets(df, pd.Series([50, 80], index=[2, 0]))
    same(out["target"].tolist(), [50, 80, None, 50])
    assert n == 1


def test_lookup_by_customer_not_by_row_number():
    df, targets = case()
    out, _ = attach_targets(df, targets)
    same(out["target"].tolist(), plain(df, targets))
    assert out["target"].tolist()[0] == 50, (
        "row 0 belongs to customer 2 (target 50). Assigning the Series directly matches row labels with customer ids: map the ids instead (df['customer_id'].map(targets)).")


def test_missing_customers_are_counted_by_rows():
    df, targets = case()
    out, n = attach_targets(df, targets)
    assert n == 1 and type(n) is int, "one row (customer 7) has no target; n_missing = %r." % (n,)
    df2 = pd.DataFrame({"customer_id": [7, 7, 8, 1]})
    _, n2 = attach_targets(df2, targets)
    assert n2 == 3, "count ROWS without a target (two rows of customer 7, one of 8), got %r." % (n2,)


def test_a_target_that_is_itself_missing_is_not_counted_as_absent_customer():
    df = pd.DataFrame({"customer_id": [1, 2]})
    targets = pd.Series([None, 5.0], index=[1, 2])
    out, n = attach_targets(df, targets)
    assert n == 0, "customer 1 IS in targets (its value is just missing): n_missing counts customers that are absent."
    assert pd.isna(out["target"].iloc[0]) and out["target"].iloc[1] == 5.0


def test_inputs_not_changed_and_other_columns_kept():
    df, targets = case()
    df0, t0 = df.copy(), targets.copy()
    out, _ = attach_targets(df, targets)
    pd.testing.assert_frame_equal(df, df0, obj="the input frame")
    pd.testing.assert_series_equal(targets, t0, obj="the targets Series")
    assert out.columns.tolist() == ["customer_id", "amount", "target"]
    assert out["amount"].tolist() == [10, 20, 30, 40, 50, 60]


def test_works_with_a_shuffled_row_index():
    df = pd.DataFrame({"customer_id": [3, 1]}, index=[1, 3])
    targets = pd.Series({1: 100, 3: 300})
    out, n = attach_targets(df, targets)
    assert out["target"].tolist() == [300, 100] and n == 0, "rows are looked up by customer id; the row labels (1, 3) are a trap."
