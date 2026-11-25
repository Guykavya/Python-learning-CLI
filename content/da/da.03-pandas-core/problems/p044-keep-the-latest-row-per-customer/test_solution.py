import numpy as np
import pandas as pd

from solution import latest_per_customer


def slow(df):
    best = {}
    for r in df.itertuples():
        key = (r.ts, r.row_id)
        if r.customer not in best or key > best[r.customer][0]:
            best[r.customer] = (key, r.row_id)
    return sorted(best.items(), key=lambda kv: kv[0])


def check(df, what):
    before = df.copy()
    got, removed = latest_per_customer(df)
    pd.testing.assert_frame_equal(df, before, obj="the input frame (it must not change)")
    assert isinstance(got, pd.DataFrame), f"{what}: the first result must be a DataFrame, got {type(got).__name__}."
    want = slow(df)
    assert got["customer"].tolist() == [c for c, _ in want], (
        f"{what}: one row per customer, ordered A to Z; expected {[c for c, _ in want]}, got {got['customer'].tolist()}.")
    assert got["row_id"].tolist() == [v[1] for _, v in want], (
        f"{what}: wrong rows kept: expected row_ids {[v[1] for _, v in want]}, got {got['row_id'].tolist()}. "
        "Latest ts wins; on the same ts the larger row_id wins.")
    assert got.index.tolist() == list(range(len(got))), f"{what}: reset the index to 0, 1, 2, ... (got {got.index.tolist()})."
    assert got.columns.tolist() == df.columns.tolist(), f"{what}: keep all columns in the same order."
    assert isinstance(removed, (int, np.integer)) and removed == len(df) - len(want), (
        f"{what}: removed should be {len(df) - len(want)} (rows in minus rows out), got {removed!r}.")


def test_the_example():
    df = pd.DataFrame({
        "row_id": [1, 2, 3, 4, 5],
        "customer": ["Ben", "Asha", "Ben", "Asha", "Ben"],
        "ts": pd.to_datetime(["2025-03-01", "2025-03-01", "2025-03-05", "2025-03-01", "2025-03-05"]),
        "amount": [10, 20, 30, 40, 50],
    })
    check(df, "example")
    got, removed = latest_per_customer(df)
    assert got["row_id"].tolist() == [4, 5] and removed == 3, (
        f"Asha has two events at the same time (rows 2 and 4): the larger row_id, 4, wins. Ben's newest are rows 3 and 5: 5 wins. Got {got['row_id'].tolist()}, removed {removed}.")


def test_rows_arrive_in_a_shuffled_order():
    df = pd.DataFrame({
        "row_id": [9, 3, 7, 1],
        "customer": ["Cy", "Cy", "Cy", "Cy"],
        "ts": pd.to_datetime(["2025-01-02", "2025-01-09", "2025-01-05", "2025-01-01"]),
        "amount": [1, 2, 3, 4],
    }, index=[40, 30, 20, 10])
    got, removed = latest_per_customer(df)
    assert got["row_id"].tolist() == [3] and removed == 3, (
        f"the newest event is row 3 (2025-01-09) even though it is not last in the table; got {got['row_id'].tolist()}, removed {removed}.")


def test_one_row_per_customer_changes_nothing():
    df = pd.DataFrame({"row_id": [2, 1], "customer": ["B", "A"], "ts": pd.to_datetime(["2025-01-01", "2025-01-01"]), "amount": [5, 6]})
    got, removed = latest_per_customer(df)
    assert got["customer"].tolist() == ["A", "B"] and removed == 0, f"already one row each: only the order changes (A to Z); got {got['customer'].tolist()}, removed {removed}."


def test_random_tables_with_many_ties():
    rng = np.random.default_rng(44)
    for trial in range(15):
        n = int(rng.integers(5, 60))
        df = pd.DataFrame({
            "row_id": rng.permutation(n) + 100,
            "customer": rng.choice(["Asha", "Ben", "Chitra", "Dev", "Esha"], n),
            "ts": pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 4, n), unit="D"),
            "amount": rng.integers(1, 100, n),
        })
        check(df, f"random table {trial}")
