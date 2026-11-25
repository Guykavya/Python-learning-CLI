import pandas as pd
import pytest

from solution import cash_vs_work

L1 = "completed in month, paid before the month"
L2 = "completed in month, paid after the month"
L3 = "completed in month, not paid yet"
L4 = "paid in month, job completed earlier"
L5 = "paid in month, job completed later or pending"
L6 = "paid in month, other jobs"
L7 = "refunds issued in month"

# jobs (job_id, status, completed_at, quote_total): one row per bucket of the bridge for February 2025
JOBS = [
    (1, "completed", "2025-02-10 09:00:00", 2000),   # deposit 500 in January, balance 1500 in February
    (2, "completed", "2025-02-01 00:00:00", 1000),   # completed exactly at the start (IN); paid exactly at the start (IN)
    (3, "completed", "2025-02-20 09:00:00", 1500),   # paid exactly at the END of February (OUT): paid after
    (4, "completed", "2025-02-25 09:00:00", 800),    # never paid: not paid yet
    (5, "completed", "2025-01-31 23:59:59", 3000),   # completed one second before February; balance 1000 paid in February
    (6, "pending", None, 600),                       # pending, but paid a deposit of 200 in February
    (7, "completed", "2025-03-02 09:00:00", 900),    # completed in March; deposit 300 paid in the last second of February
    (8, "cancelled", None, 400),                     # cancelled, but 100 was paid in February: other jobs
    (9, "completed", "2025-03-01 00:00:00", 700),    # completed exactly at the end of February (OUT); no payments
]
PAYMENTS = [
    (1, 1, "2025-01-28 09:00:00", 500), (2, 1, "2025-02-12 09:00:00", 1500),
    (3, 2, "2025-02-01 00:00:00", 1000),
    (4, 3, "2025-03-01 00:00:00", 1500),
    (5, 5, "2025-01-15 09:00:00", 2000), (6, 5, "2025-02-03 09:00:00", 1000),
    (7, 6, "2025-02-15 09:00:00", 200),
    (8, 7, "2025-02-28 23:59:59", 300),
    (9, 8, "2025-02-05 09:00:00", 100),
]
REFUNDS = [
    (1, 1, "2025-02-15 09:00:00", 250),     # in February
    (2, 5, "2025-03-01 00:00:00", 400),     # exactly at the end: March
    (3, 3, "2025-02-28 23:59:59", 150),     # in February, last second
]


def tables():
    j = pd.DataFrame(JOBS, columns=["job_id", "status", "completed_at", "quote_total"])
    j["completed_at"] = pd.to_datetime(j["completed_at"])
    p = pd.DataFrame(PAYMENTS, columns=["payment_id", "job_id", "paid_at", "amount"])
    p["paid_at"] = pd.to_datetime(p["paid_at"])
    r = pd.DataFrame(REFUNDS, columns=["refund_id", "job_id", "refunded_at", "amount"])
    r["refunded_at"] = pd.to_datetime(r["refunded_at"])
    return j, p, r


def test_february_totals():
    r = cash_vs_work(*tables(), "2025-02-01", "2025-03-01")
    assert r["work_value"] == 5300, "work completed in February: jobs 1, 2, 3, 4 = 2000 + 1000 + 1500 + 800 = 5,300 (job 5 is January, job 9 is March). Got %s." % r["work_value"]
    assert r["cash_gross"] == 4100, "payments in February: 1500 + 1000 + 1000 + 200 + 300 + 100 = 4,100. Got %s." % r["cash_gross"]
    assert r["refunds"] == 400 and r["net_cash"] == 3700, "refunds in February: 250 + 150 = 400, net cash 3,700. Got %s / %s." % (r["refunds"], r["net_cash"])


def test_february_bridge_steps():
    r = cash_vs_work(*tables(), "2025-02-01", "2025-03-01")
    assert r["steps"] == [(L1, -500), (L2, -1500), (L3, -800), (L4, 1000), (L5, 500), (L6, 100), (L7, -400)], (
        "expected -500 (job 1 deposit), -1500 (job 3, paid exactly at the end), -800 (job 4), +1000 (job 5 balance), "
        "+500 (jobs 6 and 7), +100 (job 8), -400 (refunds). Got %s." % r["steps"])
    assert r["closes"] is True and 5300 + sum(a for _, a in r["steps"]) == 3700, "work value plus the steps must equal the net cash."


def test_the_job_ids_behind_every_line():
    r = cash_vs_work(*tables(), "2025-02-01", "2025-03-01")
    assert r["ids"] == {L1: [1], L2: [3], L3: [4], L4: [5], L5: [6, 7], L6: [8], L7: [1, 3]}, (
        "every line lists the jobs behind it, sorted. Got %s." % r["ids"])


def test_march_uses_the_same_rules_and_boundaries():
    r = cash_vs_work(*tables(), "2025-03-01", "2025-04-01")
    assert r["work_value"] == 1600, "March work: job 9 (exactly at the start) and job 7 = 700 + 900. Got %s." % r["work_value"]
    assert r["cash_gross"] == 1500 and r["refunds"] == 400 and r["net_cash"] == 1100, (
        "March: payment of job 3 exactly at the start (1,500), refund of job 5 exactly at the start (400). Got %s." % {k: r[k] for k in ("cash_gross", "refunds", "net_cash")})
    assert r["steps"] == [(L1, -300), (L2, 0), (L3, -1300), (L4, 1500), (L5, 0), (L6, 0), (L7, -400)], "March steps. Got %s." % r["steps"]
    assert r["ids"][L3] == [7, 9] and r["ids"][L4] == [3] and r["ids"][L7] == [5], "ids of March: not paid yet 7 and 9 (job 7 is only part paid), job 3, job 5. Got %s." % r["ids"]
    assert r["closes"] is True


def test_empty_month_all_zero_and_inputs_untouched():
    j, p, r = tables()
    out = cash_vs_work(j, p, r, "2024-12-01", "2025-01-01")
    assert out["work_value"] == 0 and out["net_cash"] == 0 and out["closes"] is True, "a month with nothing: all zero and closes. Got %s." % out
    assert [label for label, _ in out["steps"]] == [L1, L2, L3, L4, L5, L6, L7], "all seven lines are always present, even when zero."
    assert all(v == [] for v in out["ids"].values()), "no ids when nothing happened."
    j0, p0, r0 = tables()
    pd.testing.assert_frame_equal(j, j0)
    pd.testing.assert_frame_equal(p, p0)
    pd.testing.assert_frame_equal(r, r0)


def test_types_are_plain():
    r = cash_vs_work(*tables(), pd.Timestamp("2025-02-01"), pd.Timestamp("2025-03-01"))
    assert all(type(r[k]) is int for k in ("work_value", "cash_gross", "refunds", "net_cash")), "totals are plain ints."
    assert all(type(a) is int for _, a in r["steps"]) and all(type(i) is int for v in r["ids"].values() for i in v), "amounts and ids are plain ints."
