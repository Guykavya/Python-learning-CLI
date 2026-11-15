import sqlite3

import pytest

from solution import QUERY

A = """
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, category TEXT, price REAL);
INSERT INTO books VALUES (1,'Dune','fiction',10.0),(2,'Emma','fiction',6.5),(3,'SQL Basics','tech',30.0),(4,'Python Deep','tech',40.0),(5,'Cooking','food',15.0);
"""

B = """
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, category TEXT, price REAL);
INSERT INTO books VALUES (1,'A','poetry',5.0),(2,'B','poetry',5.0),(3,'C','poetry',9.0),(4,'D','art',20.0);
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


COLS = ["category", "n_books", "avg_price"]


def test_example():
    check(QUERY, A, [("fiction", 2, 8.25), ("food", 1, 15.0), ("tech", 2, 35.0)],
          "One row per category, sorted by category; avg_price = ROUND(AVG(price), 2).", cols=COLS)


def test_other_data():
    check(QUERY, B, [("art", 1, 20.0), ("poetry", 3, 6.33)],
          "poetry has prices 5, 5, 9: the average is 19/3 = 6.333..., which ROUND(..., 2) turns into 6.33. Did you forget ROUND?", cols=COLS)
