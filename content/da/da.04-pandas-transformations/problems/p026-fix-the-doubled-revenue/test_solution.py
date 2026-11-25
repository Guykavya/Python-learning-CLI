import random

import pandas as pd
import pytest

from solution import revenue_report


def orders():
    return pd.DataFrame({
        "order_id": [1001, 1002, 1003, 1004, 1005],
        "customer_id": ["C1", "C2", "C1", "C3", "C4"],
        "amount": [100.0, 250.0, 80.0, 40.0, 60.0],
    })


def payments():
    return pd.DataFrame({
        "payment_id": ["X1", "X2", "X3", "X4", "X5", "X6", "X7", "X8", "X9"],
        "order_id": [1001, 1001, 1002, 1002, 1003, 1005, 1005, 1005, 9999],
        "status": ["failed", "paid", "paid", "paid", "pending", "failed", "failed", "paid", "paid"],
        "paid_amount": [0.0, 100.0, 125.0, 125.0, 0.0, 0.0, 0.0, 60.0, 30.0],
    })


def report():
    r = revenue_report(orders(), payments())
    assert set(r) == {"total_revenue", "orders", "paid_orders", "table"}, "return a dict with the four keys."
    return r


def test_symptom1_total_revenue_counts_each_order_once():
    total = report()["total_revenue"]
    assert total == pytest.approx(530.0), (
        "total_revenue must equal the orders' own total, 530. Got %s: merging orders with SEVERAL payments per order "
        "repeats each order once per payment (fan-out), so its amount is summed again. Aggregate the payments to one "
        "row per order BEFORE the merge." % total)
    assert type(total) is float


def test_symptom2_row_count_of_the_base_table_is_preserved():
    r = report()
    assert r["orders"] == 5, "orders must be the number of orders (5), got %s." % r["orders"]
    assert len(r["table"]) == 5, (
        "golden rule: the report table has one row per order (5), got %d. Count the rows before and after the "
        "merge, and use validate='1:1' once payments are aggregated." % len(r["table"]))
    assert r["table"]["order_id"].tolist() == [1001, 1002, 1003, 1004, 1005], "orders in the original order, each once."
    assert r["table"].index.tolist() == [0, 1, 2, 3, 4], "index 0..n-1."


def test_symptom3_paid_orders_counts_orders_not_payments():
    assert report()["paid_orders"] == 3, (
        "3 orders (1001, 1002, 1005) have at least one paid attempt. 1002 was paid in two parts: still ONE paid order. "
        "Use any() of 'status == paid' per order.")


def test_payment_status_still_reported():
    t = report()["table"]
    assert list(t.columns) == ["order_id", "customer_id", "amount", "n_payments", "paid"], (
        "columns must be order_id, customer_id, amount, n_payments, paid. Got %s." % list(t.columns))
    assert t["n_payments"].tolist() == [2, 2, 1, 0, 3], (
        "n_payments = attempts per order; 1004 has none, so 0 (not missing). Got %s." % t["n_payments"].tolist())
    assert pd.api.types.is_integer_dtype(t["n_payments"]), "n_payments must be integers (fillna(0).astype(int))."
    assert t["paid"].tolist() == [True, True, False, False, True], (
        "paid: True if any attempt is 'paid'. 1003 is only pending, 1004 has no attempt. Got %s." % t["paid"].tolist())
    assert t["paid"].dtype == bool, "paid must be a bool column (missing -> False). Got %s." % t["paid"].dtype


def test_orphan_payment_ignored():
    t = report()["table"]
    assert 9999 not in set(t["order_id"]), "payment X9 refers to order 9999, which does not exist: ignore it."


def test_no_payments_at_all():
    empty = payments().iloc[:0]
    r = revenue_report(orders(), empty)
    assert r["total_revenue"] == pytest.approx(530.0) and r["orders"] == 5 and r["paid_orders"] == 0
    assert r["table"]["n_payments"].tolist() == [0] * 5


def test_random_against_a_loop():
    rnd = random.Random(26)
    o = pd.DataFrame({"order_id": range(1, 61), "customer_id": ["C%d" % rnd.randint(1, 9) for _ in range(60)],
                      "amount": [float(rnd.randint(10, 300)) for _ in range(60)]})
    rows = []
    for k in range(150):
        rows.append(("Y%d" % k, rnd.randint(1, 70), rnd.choice(["paid", "failed", "pending"]), 1.0))
    p = pd.DataFrame(rows, columns=["payment_id", "order_id", "status", "paid_amount"])
    paid_ids = {oid for _, oid, st, _ in rows if st == "paid"}
    r = revenue_report(o, p)
    assert r["total_revenue"] == pytest.approx(sum(o["amount"])), "total must equal the order total on random data."
    assert r["orders"] == 60 and len(r["table"]) == 60
    assert r["paid_orders"] == len(paid_ids & set(range(1, 61))), "paid_orders differs from a plain loop."


def test_inputs_not_changed():
    o, p = orders(), payments()
    ob, pb = o.copy(), p.copy()
    revenue_report(o, p)
    pd.testing.assert_frame_equal(o, ob, obj="the input orders")
    pd.testing.assert_frame_equal(p, pb, obj="the input payments")
