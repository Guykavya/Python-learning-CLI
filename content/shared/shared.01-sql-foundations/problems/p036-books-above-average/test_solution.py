import sqlite3

import pytest

from solution import QUERY

A = """
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL);
INSERT INTO books VALUES (1,'Dune',10.0),(2,'Emma',6.0),(3,'SQL Basics',30.0),(4,'Python Deep',40.0),(5,'Cooking',15.0),(6,'Algorithms',50.0);
"""

B = """
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL);
INSERT INTO books VALUES (1,'a',10.0),(2,'b',20.0),(3,'c',30.0);
"""

C = """
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL);
INSERT INTO books VALUES (1,'a',7.0),(2,'b',7.0);
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


COLS = ["title", "price"]


def test_example():
    check(QUERY, A, [("Algorithms", 50.0), ("Python Deep", 40.0), ("SQL Basics", 30.0)],
          "The average is about 25.17; keep books priced above it, most expensive first.", cols=COLS)


def test_equal_to_average_excluded():
    check(QUERY, B, [("c", 30.0)],
          "The average is exactly 20.0. A book priced 20.0 is NOT above the average: use > not >=.", cols=COLS)


def test_all_equal():
    check(QUERY, C, [],
          "When every price equals the average, no book is above it: the result is empty.", cols=COLS)


def test_uses_subquery():
    assert QUERY.upper().count("SELECT") >= 2, "Use a scalar subquery (SELECT AVG(price) FROM books) instead of a hard-coded number."
