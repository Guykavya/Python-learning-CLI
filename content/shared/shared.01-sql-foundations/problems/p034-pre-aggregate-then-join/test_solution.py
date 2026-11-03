import sqlite3

import pytest

from solution import QUERY

A = """
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT);
INSERT INTO orders VALUES (101,1,'2024-01-05'),(102,1,'2024-02-10'),(103,4,'2024-02-11');
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES (101,1,2,10.0),(101,3,1,30.0),(102,4,1,40.0),(103,5,1,15.0);
CREATE TABLE payments (payment_id INTEGER PRIMARY KEY, order_id INTEGER, amount REAL);
INSERT INTO payments VALUES (1,101,30.0),(2,101,20.0),(3,102,40.0);
"""

B = """
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT);
INSERT INTO orders VALUES (1,1,'2024-01-01'),(2,1,'2024-01-02'),(3,2,'2024-01-03'),(4,2,'2024-01-04');
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES (1,1,1,10.0),(1,2,1,5.0),(1,3,2,2.5),(3,1,1,10.0);
CREATE TABLE payments (payment_id INTEGER PRIMARY KEY, order_id INTEGER, amount REAL);
INSERT INTO payments VALUES (1,1,5.0),(2,1,5.0),(3,1,10.0),(4,2,4.0);
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


COLS = ["order_id", "items_total", "paid"]


def test_example():
    check(QUERY, A, [(101, 50.0, 50.0), (102, 40.0, 40.0), (103, 15.0, 0.0)],
          "Order 101 has 2 lines and 2 payments: a plain double join pairs every line with every payment and doubles both sums. Summarise each side per order_id first. Orders without payments get 0.0.",
          cols=COLS)


def test_missing_sides():
    check(QUERY, B, [(1, 20.0, 20.0), (2, 0.0, 4.0), (3, 10.0, 0.0), (4, 0.0, 0.0)],
          "Order 2 has no lines (items_total 0.0), order 3 no payments (paid 0.0), order 4 neither. Use LEFT JOIN and COALESCE(..., 0.0). Order 1: 3 lines x 3 payments must not multiply.",
          cols=COLS)
