import random

import pandas as pd
import pytest

from solution import running_spend


def orders():
    return pd.DataFrame({
        "order_id": [6, 3, 5, 1, 4, 2],
        "customer_id": ["C", "A", "B", "A", "B", "A"],
        "order_date": pd.to_datetime(["2025-03-01", "2025-01-05", "2025-01-01", "2025-01-02", "2025-02-01", "2025-01-05"]),
        "amount": [100.0, 10.0, 3.0, 20.0, 7.0, 5.0],
    }, index=[9, 8, 7, 6, 5, 4])


def test_sorted_and_reindexed():
    out = running_spend(orders())
    assert out["order_id"].tolist() == [1, 2, 3, 5, 4, 6], (
        "sort by customer_id, then order_date, then order_id: A(1, 2, 3), B(5 on Jan 1, then 4), C(6). "
        "Got %s." % out["order_id"].tolist())
    assert out.index.tolist() == list(range(6)), "index 0..n-1 after sorting (ignore_index=True or reset_index(drop=True))."
    assert list(out.columns) == ["order_id", "customer_id", "order_date", "amount", "running_spend"]


def test_running_total_restarts_per_customer():
    got = running_spend(orders())["running_spend"].tolist()
    assert got == pytest.approx([20.0, 25.0, 35.0, 3.0, 10.0, 100.0]), (
        "running_spend must restart for every customer: groupby('customer_id')['amount'].cumsum(). A plain cumsum "
        "of the column carries A's total into B. Got %s." % got)


def test_sort_before_cumsum():
    got = running_spend(orders())
    b = got[got["customer_id"] == "B"]["running_spend"].tolist()
    assert b == pytest.approx([3.0, 10.0]), (
        "B's first order by date is order 5 (3.0), so B's running totals are 3 then 10. If you get 7 then 10, the "
        "cumsum ran before sorting by date.")


def test_last_value_is_customer_total():
    df = orders()
    out = running_spend(df)
    last = out.groupby("customer_id")["running_spend"].last()
    total = df.groupby("customer_id")["amount"].sum()
    assert last.tolist() == pytest.approx(total.tolist()), "each customer's last running total equals their total spend."


def test_random_against_a_loop():
    rnd = random.Random(8)
    n = 120
    df = pd.DataFrame({
        "order_id": rnd.sample(range(1000, 2000), n),
        "customer_id": [rnd.choice("ABCDE") for _ in range(n)],
        "order_date": pd.to_datetime("2025-01-01") + pd.to_timedelta([rnd.randint(0, 30) for _ in range(n)], unit="D"),
        "amount": [float(rnd.randint(1, 99)) for _ in range(n)],
    })
    rows = sorted(zip(df["customer_id"], df["order_date"], df["order_id"], df["amount"]))
    want, run, prev = [], 0.0, None
    for c, _, _, a in rows:
        run = a if c != prev else run + a
        prev = c
        want.append(run)
    out = running_spend(df)
    assert out["order_id"].tolist() == [r[2] for r in rows], "row order differs from sorting by (customer, date, order_id)."
    assert out["running_spend"].tolist() == pytest.approx(want), "running totals differ from a plain loop."


def test_input_not_changed():
    df = orders()
    before = df.copy()
    running_spend(df)
    pd.testing.assert_frame_equal(df, before, obj="the input orders (sort a copy, not in place)")
