import sqlite3

import pytest

from solution import QUERY_A, QUERY_B

A = """
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES
 (101,1,'2024-01-05','shipped'),(102,1,'2024-02-10','shipped'),(103,4,'2024-02-11','cancelled'),
 (104,2,'2024-03-01','shipped'),(105,3,'2024-03-15','shipped');
"""

B = """
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES (1,9,'2024-01-01','shipped'),(2,9,'2024-01-02','returned'),(3,8,'2024-01-03','cancelled'),(4,8,'2024-01-04','cancelled'),(5,7,'2024-01-05','shipped'),(6,7,'2024-01-06','shipped'),(7,7,'2024-01-07','shipped');
"""


def connect(schema):
    con = sqlite3.connect(":memory:")
    con.executescript(schema)
    return con


def run(con, sql):
    """Run ONE query. Return (column names, rows). Fail clearly if SQLite rejects it."""
    try:
        cur = con.execute(sql)
    except (sqlite3.Error, sqlite3.Warning) as e:
        pytest.fail(f"SQLite rejected your query: {e}. Write exactly one statement, no trailing second statement.")
    if cur.description is None:
        pytest.fail("Your query returned no result set. Write a SELECT (or WITH ... SELECT).")
    return [d[0] for d in cur.description], cur.fetchall()


def check(sql, schema, want, msg, ordered=True, cols=None):
    con = connect(schema)
    names, got = run(con, sql)
    if cols is not None:
        assert names == cols, f"Column names/order must be {cols}, you returned {names}. Use AS to name them."
    if not ordered:
        got, want = sorted(got, key=repr), sorted(want, key=repr)
    assert got == want, f"{msg} Expected {want} but got {got}."


COLS = ["customer_id", "total", "shipped", "cancelled"]
WANT_A = [(1, 2, 2, 0), (2, 1, 1, 0), (3, 1, 1, 0), (4, 1, 0, 1)]
WANT_B = [(7, 3, 3, 0), (8, 2, 0, 2), (9, 2, 1, 0)]


@pytest.mark.parametrize("name,sql", [("QUERY_A", QUERY_A), ("QUERY_B", QUERY_B)])
def test_example(name, sql):
    check(sql, A, WANT_A,
          f"{name}: one row per customer. Customer 4 has a single cancelled order -> (4, 1, 0, 1). Use 0, not NULL, when nothing matches.", cols=COLS)


@pytest.mark.parametrize("name,sql", [("QUERY_A", QUERY_A), ("QUERY_B", QUERY_B)])
def test_other_statuses(name, sql):
    check(sql, B, WANT_B,
          f"{name}: customer 9 has a 'returned' order that counts in total but in neither shipped nor cancelled. Customer 7 has 0 cancelled (not NULL).", cols=COLS)


def test_query_shapes():
    assert "CASE" in QUERY_A.upper(), "QUERY_A must use SUM(CASE WHEN ...)."
    assert "FILTER" in QUERY_B.upper(), "QUERY_B must use the FILTER (WHERE ...) clause."
