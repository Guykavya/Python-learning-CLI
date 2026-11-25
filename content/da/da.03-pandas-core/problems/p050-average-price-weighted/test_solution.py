import numpy as np
import pandas as pd
import pytest

from solution import summary_numbers


def slow(df):
    rev = 0.0
    units = 0
    for q, p in zip(df["qty"], df["unit_price"]):
        rev += q * p
        units += q
    return {"orders": len(df), "units": units, "revenue": rev, "avg_price": rev / units if units else None}


def check(df, what):
    before = df.copy()
    got = summary_numbers(df)
    pd.testing.assert_frame_equal(df, before, obj="the input frame")
    want = slow(df)
    assert isinstance(got, dict), f"{what}: return a dict, not a {type(got).__name__}."
    assert set(got) == set(want), f"{what}: keys should be {sorted(want)}, got {sorted(got)}."
    assert got["orders"] == want["orders"] and isinstance(got["orders"], int), f"{what}: orders should be the int {want['orders']}, got {got['orders']!r}."
    assert got["units"] == want["units"], f"{what}: units should be {want['units']}, got {got['units']!r}."
    assert got["revenue"] == pytest.approx(want["revenue"]), f"{what}: revenue should be the sum of qty * unit_price = {want['revenue']}, got {got['revenue']!r}."
    if want["avg_price"] is None:
        assert got["avg_price"] is None, f"{what}: nothing sold, so avg_price should be None, got {got['avg_price']!r}."
    else:
        assert got["avg_price"] == pytest.approx(want["avg_price"]), (
            f"{what}: avg_price should be revenue / units = {want['avg_price']}, got {got['avg_price']!r}.")


def test_the_example_and_the_unweighted_trap():
    df = pd.DataFrame({"order_id": [1, 2, 3], "qty": [1, 1, 10], "unit_price": [100.0, 100.0, 10.0]})
    check(df, "example")
    got = summary_numbers(df)
    assert got["avg_price"] != pytest.approx(70.0), (
        "70.0 is the plain mean of the three prices (100 + 100 + 10) / 3: that counts the price of 1 unit as much as the price of 10 units. "
        "The weighted average is 300 / 12 = 25.0.")
    assert got["avg_price"] == pytest.approx(25.0), f"expected 25.0, got {got['avg_price']!r}."


def test_one_row():
    check(pd.DataFrame({"order_id": [5], "qty": [4], "unit_price": [2.5]}), "one row")


def test_empty_table():
    df = pd.DataFrame({"order_id": pd.Series([], dtype="int64"), "qty": pd.Series([], dtype="int64"),
                       "unit_price": pd.Series([], dtype="float64")})
    got = summary_numbers(df)
    assert got["orders"] == 0 and got["units"] == 0 and got["revenue"] == 0.0 and got["avg_price"] is None, (
        f"an empty table gives orders 0, units 0, revenue 0.0 and avg_price None (no division by zero); got {got}.")


def test_random_tables():
    rng = np.random.default_rng(50)
    for i in range(10):
        n = int(rng.integers(1, 200))
        df = pd.DataFrame({"order_id": np.arange(n), "qty": rng.integers(1, 20, n), "unit_price": rng.gamma(4.0, 120.0, n).round(2)})
        check(df, f"random table {i}")
