import sqlite3

import pytest

from solution import QUERY

A = """
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, category TEXT, price REAL NOT NULL);
INSERT INTO books VALUES
 (1,'Dune','fiction',10.0),(2,'Emma','fiction',6.0),(3,'SQL Basics','tech',30.0),
 (4,'Python Deep','tech',40.0),(5,'Cooking','food',15.0),(6,'Algorithms','tech',50.0);
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES
 (101,1,2,10.0),(101,3,1,30.0),(102,4,1,40.0),(103,5,1,15.0),
 (104,2,3,6.0),(104,3,1,30.0),(105,6,1,50.0),(105,3,1,28.0);
"""

B = """
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, category TEXT, price REAL NOT NULL);
INSERT INTO books VALUES (1,'a','x',1.0),(2,'b','x',1.0),(3,'c','x',1.0),(4,'d','x',1.0);
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES (1,1,1,1.0),(1,2,1,1.0),(2,2,1,1.0),(2,3,5,1.0);
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


COLS = ["title", "units"]


def test_example():
    check(QUERY, A, [("Emma", 3), ("SQL Basics", 3), ("Dune", 2)],
          "units is SUM(qty), not the number of lines. Emma: one line of 3. SQL Basics: three lines of 1. Keep units >= 2; ties sorted by title.", cols=COLS)


def test_other_data():
    check(QUERY, B, [("c", 5), ("b", 2)],
          "Book b: two lines of qty 1 gives 2 units (kept, boundary). Book a: 1 unit (dropped). Book d: never ordered (absent).", cols=COLS)


def test_uses_cte():
    assert QUERY.upper().lstrip().startswith("WITH") or "\nWITH " in QUERY.upper(), "Use a CTE: WITH book_sales AS (...) SELECT ..."
