import sqlite3

import pytest

from solution import QUERY

A = """
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES (1,1,'2024-01-01','shipped'),(2,1,'2024-01-09','shipped'),(3,1,'2024-02-01','cancelled'),(4,2,'2024-02-03','shipped'),(5,2,'2024-02-05','shipped'),(6,2,'2024-02-07','shipped'),(7,3,'2024-03-01','cancelled'),(8,3,'2024-03-02','cancelled');
"""

B = """
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES (1,7,'2024-01-01','pending'),(2,7,'2024-01-02','pending'),(3,5,'2024-01-03','shipped'),(4,5,'2024-01-03','shipped'),(5,6,'2024-01-04','shipped'),(6,6,'2024-01-04','pending');
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


COLS = ["customer_id", "status", "n_orders"]


def test_example():
    check(QUERY, A, [(2, "shipped", 3), (3, "cancelled", 2), (1, "shipped", 2), (1, "cancelled", 1)],
          "Group by BOTH customer_id and status. Sort n_orders DESC, then customer_id DESC, then status ASC.", cols=COLS)


def test_ties_use_tie_breakers():
    check(QUERY, B, [(7, "pending", 2), (5, "shipped", 2), (6, "pending", 1), (6, "shipped", 1)],
          "Customers 7 and 5 tie on 2 orders (larger customer_id first); customer 6 has two pairs with 1 order, so status breaks the tie.", cols=COLS)
