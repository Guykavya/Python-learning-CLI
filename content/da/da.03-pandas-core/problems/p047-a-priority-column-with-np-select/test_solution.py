import numpy as np
import pandas as pd

from solution import priority


def rule(days, amount, vip):
    if days > 30:
        return "urgent"
    if vip and days > 0:
        return "high"
    if amount >= 5000:
        return "medium"
    return "low"


def test_the_example_and_order_of_rules():
    df = pd.DataFrame({
        "overdue_days": [40, 3, 0, 0, 10],
        "amount": [100, 100, 6000, 100, 6000],
        "vip": [True, True, False, True, False],
    })
    before = df.copy()
    got = priority(df)
    pd.testing.assert_frame_equal(df, before, obj="the input frame")
    assert isinstance(got, pd.Series), f"return a Series, not a {type(got).__name__}."
    assert got.name == "priority", f"the Series must be named 'priority', got {got.name!r}."
    assert got.tolist() == ["urgent", "high", "medium", "low", "medium"], (
        f"expected ['urgent', 'high', 'medium', 'low', 'medium'], got {got.tolist()}. "
        "A VIP 40 days overdue is 'urgent' (rule 1 comes first); a VIP who is not overdue is not 'high' (rule 2 needs days > 0).")


def test_boundaries():
    df = pd.DataFrame({
        "overdue_days": [30, 31, 1, 0, 0],
        "amount": [0, 0, 0, 5000, 4999],
        "vip": [False, False, True, False, False],
    })
    got = priority(df)
    assert got.tolist() == ["low", "urgent", "high", "medium", "low"], (
        f"30 days is not > 30; amount 5000 is >= 5000; got {got.tolist()}.")


def test_index_is_kept():
    df = pd.DataFrame({"overdue_days": [0, 50], "amount": [1, 1], "vip": [False, False]}, index=[7, 3])
    got = priority(df)
    assert got.index.tolist() == [7, 3], "keep the index of the input."


def test_random_frame_against_the_plain_function():
    rng = np.random.default_rng(47)
    n = 500
    df = pd.DataFrame({
        "overdue_days": rng.integers(0, 60, n),
        "amount": rng.integers(0, 10000, n),
        "vip": rng.random(n) < 0.3,
    })
    got = priority(df)
    want = [rule(d, a, v) for d, a, v in zip(df["overdue_days"], df["amount"], df["vip"])]
    assert got.tolist() == want, "some rows differ from the if / elif version of the rules."
    assert set(got.unique()) == {"urgent", "high", "medium", "low"}, "all four labels should occur in a table this size."
