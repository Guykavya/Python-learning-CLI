import random

import pandas as pd

from solution import busy_customers


def orders():
    return pd.DataFrame({
        "order_id": [101, 102, 103, 104, 105, 106, 107, 108, 109],
        "customer_id": ["B", "A", "C", "B", "A", "B", "D", "C", "A"],
        "store_id": ["S1", "S2", "S1", "S1", "S3", "S2", "S1", "S2", "S1"],
    }, index=[20, 21, 22, 23, 24, 25, 26, 27, 28])


def test_three_or_more():
    out = busy_customers(orders(), 3)
    assert out.index.tolist() == [20, 21, 23, 24, 25, 28], (
        "A and B have 3 orders each: keep ALL their rows, in the original order and with the original index. "
        "Got index %s." % out.index.tolist())
    assert set(out["customer_id"]) == {"A", "B"}


def test_at_least_means_equal_counts():
    out = busy_customers(orders(), 2)
    assert sorted(out["customer_id"].unique()) == ["A", "B", "C"], (
        "'at least 2' includes customers with exactly 2 orders (C): use >=, not >.")
    assert len(out) == 8, "D (one order) is the only customer dropped."


def test_whole_rows_and_columns_kept():
    df = orders()
    out = busy_customers(df, 3)
    assert list(out.columns) == list(df.columns), "keep every column: filter returns the original rows."
    pd.testing.assert_frame_equal(out, df.loc[[20, 21, 23, 24, 25, 28]], obj="the rows of A and B")


def test_nobody_qualifies():
    df = orders()
    out = busy_customers(df, 10)
    assert len(out) == 0, "nobody has 10 orders: the result is empty."
    assert list(out.columns) == list(df.columns), "an empty result still has the same columns."


def test_everybody_qualifies():
    df = orders()
    pd.testing.assert_frame_equal(busy_customers(df, 1), df, obj="min_orders=1 keeps every row")


def test_random_against_a_loop():
    rnd = random.Random(3)
    df = pd.DataFrame({"order_id": range(200), "customer_id": [rnd.choice("ABCDEFGHIJ") for _ in range(200)],
                       "store_id": ["S1"] * 200})
    counts = {}
    for c in df["customer_id"]:
        counts[c] = counts.get(c, 0) + 1
    for k in [15, 20, 25]:
        want = [i for i, c in zip(df.index, df["customer_id"]) if counts[c] >= k]
        assert busy_customers(df, k).index.tolist() == want, "min_orders=%d: the kept rows differ from a plain loop." % k


def test_input_not_changed():
    df = orders()
    before = df.copy()
    busy_customers(df, 3)
    pd.testing.assert_frame_equal(df, before, obj="the input orders")
