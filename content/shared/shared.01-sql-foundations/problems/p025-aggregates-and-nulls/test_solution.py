import sqlite3

import pytest

from solution import QUERY

A = """
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, pages INTEGER);
INSERT INTO books VALUES (1,'T1',100),(2,'T2',200),(3,'T3',NULL),(4,'T4',300);
"""

B = """
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, pages INTEGER);
INSERT INTO books VALUES (1,'T1',50),(2,'T2',NULL),(3,'T3',NULL),(4,'T4',150);
"""

C = """
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, pages INTEGER);
INSERT INTO books VALUES (1,'T1',NULL),(2,'T2',NULL);
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


COLS = ["total_pages", "avg_known", "shortest", "longest", "avg_if_zero"]


def test_example():
    check(QUERY, A, [(600, 200.0, 100, 300, 150.0)],
          "AVG skips NULL (600/3 = 200.0). For avg_if_zero put COALESCE(pages, 0) INSIDE AVG so the NULL row counts as 0 (600/4 = 150.0).", cols=COLS)


def test_two_nulls():
    check(QUERY, B, [(200, 100.0, 50, 150, 50.0)],
          "Two of four values are NULL: avg_known = 200/2 = 100.0 but avg_if_zero = 200/4 = 50.0.", cols=COLS)


def test_all_null():
    check(QUERY, C, [(None, None, None, None, 0.0)],
          "With only NULLs, SUM/AVG/MIN/MAX are NULL, but AVG(COALESCE(pages, 0)) is 0.0. Do not wrap the first four in COALESCE.", cols=COLS)
