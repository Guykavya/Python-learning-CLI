import pandas as pd

from solution import dedupe_by_key


def sample():
    return pd.DataFrame({
        "email": ["a@x", "b@x", "a@x", "c@x", "b@x", "a@x"],
        "score": [3, 5, 7, 2, 6, 9],
        "sent": [10, 11, 12, 13, 9, 12],
    })


def test_largest_order_value_survives_and_labels_are_kept():
    kept, removed = dedupe_by_key(sample(), "email", "sent")
    assert kept.index.tolist() == [1, 3, 5], (
        "kept must be in the original order with the original labels: b@x -> row 1 (sent 11), c@x -> row 3, "
        "a@x -> row 5. Got %s." % kept.index.tolist())
    assert removed.index.tolist() == [0, 2, 4], "removed rows: 0, 2, 4. Got %s." % removed.index.tolist()


def test_tie_goes_to_the_later_row():
    kept, _ = dedupe_by_key(sample(), "email", "sent")
    assert kept.loc[5, "score"] == 9, "rows 2 and 5 of a@x tie on sent = 12; the LATER row (5) must survive."
    assert 2 not in kept.index


def test_kept_is_not_sorted_by_the_ordering_column():
    df = pd.DataFrame({"k": ["x", "y", "z", "x"], "t": [5, 9, 1, 7]})
    kept, _ = dedupe_by_key(df, "k", "t")
    assert kept.index.tolist() == [1, 2, 3], "keep the original row order (not the order of t). Got %s." % kept.index.tolist()


def test_one_row_per_key_and_nothing_lost():
    df = sample()
    kept, removed = dedupe_by_key(df, "email", "sent")
    assert kept["email"].is_unique, "kept must have one row per key."
    assert sorted(kept.index.tolist() + removed.index.tolist()) == df.index.tolist(), (
        "kept + removed must contain every row exactly once.")
    assert set(removed["email"]) <= set(kept["email"]), "every removed row's key must still be present in kept."


def test_columns_and_values_are_unchanged():
    kept, removed = dedupe_by_key(sample(), "email", "sent")
    assert list(kept.columns) == ["email", "score", "sent"] and list(removed.columns) == ["email", "score", "sent"]
    assert removed["score"].tolist() == [3, 7, 6]


def test_dates_as_ordering_column_and_non_default_index():
    df = pd.DataFrame(
        {"id": ["u1", "u2", "u1"], "when": pd.to_datetime(["2024-03-01", "2024-01-05", "2024-02-01"])},
        index=[100, 101, 102])
    kept, removed = dedupe_by_key(df, "id", "when")
    assert kept.index.tolist() == [100, 101], "u1: 2024-03-01 is newer than 2024-02-01. Got %s." % kept.index.tolist()
    assert removed.index.tolist() == [102]


def test_no_duplicates_means_nothing_removed():
    df = pd.DataFrame({"k": [1, 2, 3], "t": [3, 2, 1]})
    kept, removed = dedupe_by_key(df, "k", "t")
    assert kept.index.tolist() == [0, 1, 2] and len(removed) == 0, "no repeated key: keep everything, remove nothing."


def test_input_is_not_changed():
    df = sample()
    dedupe_by_key(df, "email", "sent")
    pd.testing.assert_frame_equal(df, sample(), obj="the input frame (do not sort or edit it in place)")
