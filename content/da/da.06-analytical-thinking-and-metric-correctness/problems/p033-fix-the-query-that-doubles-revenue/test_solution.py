import sqlite3

import pandas as pd
import pytest

from solution import QUERY

SCHEMA = """
CREATE TABLE jobs (job_id INTEGER PRIMARY KEY, created_at TEXT, status TEXT, quote_total INTEGER);
CREATE TABLE items (job_id INTEGER, line_no INTEGER, amount INTEGER);
CREATE TABLE payments (payment_id INTEGER PRIMARY KEY, job_id INTEGER, paid_at TEXT, amount INTEGER);
"""
JOBS = [
    (1, "2025-01-10 09:00:00", "completed", 1000),   # 3 lines, 2 payments: fans out 6 times in the buggy query
    (2, "2025-01-20 09:00:00", "completed", 1000),   # SAME quote as job 1: SUM(DISTINCT) would drop it
    (3, "2025-01-31 23:59:59", "completed", 500),    # last second of January, 1 line, 1 payment
    (4, "2025-02-01 00:00:00", "pending", 700),      # first instant of February, 2 lines, NO payment (inner join loses it)
    (5, "2025-03-05 09:00:00", "cancelled", 300),    # March: only an unpaid job, no line items at all
    (6, "2025-03-20 09:00:00", "completed", 800),    # March: 1 line, 2 payments
]
ITEMS = [(1, 1, 400), (1, 2, 400), (1, 3, 200), (2, 1, 1000), (3, 1, 500), (4, 1, 300), (4, 2, 400), (6, 1, 800)]
PAYMENTS = [(1, 1, "2025-01-11 09:00:00", 400), (2, 1, "2025-01-12 09:00:00", 600), (3, 2, "2025-01-21 09:00:00", 1000),
            (4, 3, "2025-02-01 00:00:00", 500), (5, 6, "2025-03-21 09:00:00", 300), (6, 6, "2025-03-22 09:00:00", 500)]


def connect():
    con = sqlite3.connect(":memory:")
    con.executescript(SCHEMA)
    con.executemany("INSERT INTO jobs VALUES (?,?,?,?)", JOBS)
    con.executemany("INSERT INTO items VALUES (?,?,?)", ITEMS)
    con.executemany("INSERT INTO payments VALUES (?,?,?,?)", PAYMENTS)
    return con


def run():
    con = connect()
    try:
        cur = con.execute(QUERY)
    except (sqlite3.Error, sqlite3.Warning) as e:
        pytest.fail(f"SQLite rejected your query: {e}. Write exactly one SELECT (or WITH ... SELECT).")
    return [d[0] for d in cur.description], cur.fetchall()


def pandas_truth():
    jobs = pd.DataFrame(JOBS, columns=["job_id", "created_at", "status", "quote_total"])
    pays = pd.DataFrame(PAYMENTS, columns=["payment_id", "job_id", "paid_at", "amount"])
    jobs["month"] = jobs["created_at"].str[:7]
    jobs["paid"] = jobs["job_id"].map(pays.groupby("job_id")["amount"].sum()).fillna(0)
    g = jobs.groupby("month").agg(quoted=("quote_total", "sum"), paid=("paid", "sum"))
    return [(m, int(r.quoted), int(r.paid)) for m, r in g.iterrows()]


def test_the_truth_was_counted_by_hand():
    assert pandas_truth() == [("2025-01", 2500, 2500), ("2025-02", 700, 0), ("2025-03", 1100, 800)], "test data check."


def test_columns_and_one_row_per_month():
    names, rows = run()
    assert names == ["month", "quoted", "paid"], "columns must be month, quoted, paid. Got %s." % names
    assert [r[0] for r in rows] == ["2025-01", "2025-02", "2025-03"], (
        "one row per month, sorted. February (only an unpaid job) and March (a job with no line items) must not disappear: "
        "inner joins drop jobs without payments or items. Got months %s." % [r[0] for r in rows])


def test_revenue_equals_the_pandas_truth():
    _, rows = run()
    want = pandas_truth()
    assert rows == want, (
        "expected %s but got %s. Each job must count ONCE: joining items and payments to jobs repeats the job "
        "(lines x payments) times, so aggregate the many side per job (a CTE or subquery) BEFORE joining, "
        "and use a LEFT JOIN so unpaid jobs stay." % (want, rows))


def test_no_fan_out_total():
    _, rows = run()
    assert sum(r[1] for r in rows) == sum(j[3] for j in JOBS), "the quoted values must add up to the sum of quote_total of the 6 jobs (4,300)."
    assert sum(r[2] for r in rows) == sum(p[3] for p in PAYMENTS), "the paid values must add up to the sum of all payments (3,300)."


def test_paid_is_zero_not_null_for_unpaid_months():
    _, rows = run()
    feb = [r for r in rows if r[0] == "2025-02"]
    assert feb and feb[0][2] == 0 and feb[0][2] is not None, "February has an unpaid job: paid must be 0 (COALESCE), not NULL."
