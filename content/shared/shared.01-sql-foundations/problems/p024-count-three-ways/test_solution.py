import sqlite3

import pytest

from solution import QUERY

A = """
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
INSERT INTO customers VALUES (1,'Asha','Pune'),(2,'Bala','Delhi'),(3,'Chitra',NULL),(4,'Dev','Pune'),(5,'Esha',NULL),(6,'Farid','Mumbai');
"""

B = """
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
INSERT INTO customers VALUES (1,'A','Goa'),(2,'B','Goa'),(3,'C','Goa'),(4,'D',NULL),(5,'E','Goa');
"""

C = """
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
INSERT INTO customers VALUES (1,'A',NULL),(2,'B',NULL);
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


COLS = ["total_rows", "with_city", "distinct_cities"]


def test_example_data():
    check(QUERY, A, [(6, 4, 3)],
          "Two cities are NULL and Pune appears twice: COUNT(*) counts rows, COUNT(city) skips NULL, COUNT(DISTINCT city) skips repeats.",
          cols=COLS)


def test_many_repeats():
    check(QUERY, B, [(5, 4, 1)],
          "Four customers live in Goa: distinct_cities is 1. Did you forget DISTINCT?", cols=COLS)


def test_all_null_column():
    check(QUERY, C, [(2, 0, 0)],
          "When every city is NULL, COUNT(city) and COUNT(DISTINCT city) are 0 but COUNT(*) is still the row count.", cols=COLS)
