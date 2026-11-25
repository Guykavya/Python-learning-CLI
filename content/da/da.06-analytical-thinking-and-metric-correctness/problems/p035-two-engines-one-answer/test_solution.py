import sqlite3

import pandas as pd
import pytest

from solution import both_ways

# (job_id, created_at, quote_total, why)
ROWS = [
    (1, "2025-01-31 23:59:59", 1000, "last second of January"),
    (2, "2025-02-01 00:00:00", 2000, "first instant of February (boundary: IN)"),
    (3, "2025-02-28 15:30:00", 1500, "afternoon of the last day (a closed '<= 2025-02-28' loses it)"),
    (4, "2025-03-01 00:00:00", 900, "first instant of March (boundary: OUT)"),
    (5, "2025-02-10 10:00:00", None, "no quote yet: NULL"),
]
FEB = "created_at >= '2025-02-01' AND created_at < '2025-03-01'"


@pytest.fixture
def con():
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE jobs (job_id INTEGER, created_at TEXT, quote_total INTEGER)")
    c.executemany("INSERT INTO jobs VALUES (?,?,?)", [r[:3] for r in ROWS])
    yield c
    c.close()


def pandas_feb():
    df = pd.DataFrame([r[:3] for r in ROWS], columns=["job_id", "created_at", "quote_total"])
    m = (df["created_at"] >= "2025-02-01") & (df["created_at"] < "2025-03-01")
    return int(m.sum()), float(df.loc[m, "quote_total"].sum())


def test_match_returns_the_text(con):
    n, total = pandas_feb()
    assert (n, total) == (3, 3500.0), "test data check: 3 jobs in February worth 3,500."
    got = both_ways("jobs in Feb", n, f"SELECT COUNT(*) FROM jobs WHERE {FEB}", con)
    assert got == "jobs in Feb: pandas=3.00 sql=3.00 MATCH", "wrong text on a match. Got %r." % got
    got = both_ways("value", total, f"SELECT SUM(quote_total) FROM jobs WHERE {FEB}", con)
    assert got == "value: pandas=3,500.00 sql=3,500.00 MATCH", "numbers are written with f'{x:,.2f}'. Got %r." % got


def test_mismatch_raises_with_both_numbers(con):
    with pytest.raises(AssertionError) as e:
        both_ways("jobs in Feb", 4, f"SELECT COUNT(*) FROM jobs WHERE {FEB}", con)
    assert str(e.value) == "jobs in Feb: MISMATCH pandas=4.00 sql=3.00", (
        "the message must show the name and BOTH numbers: 'name: MISMATCH pandas=4.00 sql=3.00'. Got %r." % str(e.value))


def test_a_typical_real_bug_is_caught(con):
    closed = "created_at >= '2025-02-01' AND created_at <= '2025-02-28'"
    with pytest.raises(AssertionError) as e:
        both_ways("jobs in Feb", pandas_feb()[0], f"SELECT COUNT(*) FROM jobs WHERE {closed}", con)
    assert "pandas=3.00 sql=2.00" in str(e.value), "the closed interval loses the afternoon job: SQL says 2, pandas says 3. Got %r." % str(e.value)


def test_tolerance_is_half_a_cent(con):
    sql = "SELECT 10.004"
    assert both_ways("x", 10.0, sql, con).endswith("MATCH"), "a difference of 0.004 is within the tolerance 0.005."
    with pytest.raises(AssertionError):
        both_ways("x", 10.0, "SELECT 10.006", con)


def test_null_and_empty_results_are_mismatches(con):
    with pytest.raises(AssertionError) as e:
        both_ways("avg quote of nothing", 5.0, "SELECT AVG(quote_total) FROM jobs WHERE job_id > 100", con)
    assert str(e.value) == "avg quote of nothing: MISMATCH pandas=5.00 sql=None", "a NULL result is a mismatch shown as sql=None. Got %r." % str(e.value)
    with pytest.raises(AssertionError) as e2:
        both_ways("no row", 1.0, "SELECT job_id FROM jobs WHERE job_id > 100", con)
    assert "sql=None" in str(e2.value), "a query that returns no row is also a mismatch with sql=None."
