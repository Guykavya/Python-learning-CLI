import sqlite3

import pytest

from solution import QUERY

A = """
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
INSERT INTO customers VALUES (1,'Asha','Pune'),(2,'Bala','Delhi'),(3,'Chitra',NULL),(4,'Dev','Pune');
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES
 (101,1,'2024-01-05','shipped'),(102,1,'2024-02-10','shipped'),(103,4,'2024-02-11','cancelled'),
 (104,2,'2024-03-01','shipped'),(105,3,'2024-03-15','shipped');
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES
 (101,1,2,10.0),(101,3,1,30.0),(102,4,1,40.0),(103,5,1,15.0),
 (104,2,3,6.0),(104,3,1,30.0),(105,6,1,50.0),(105,3,1,28.0);
"""

B = """
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
INSERT INTO customers VALUES (1,'Zed','X'),(2,'Amy','Y'),(3,'Max','Z');
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES (1,1,'2024-01-01','shipped'),(2,2,'2024-01-02','shipped'),(3,2,'2024-01-03','shipped');
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES (1,1,1,10.0),(1,2,2,5.0),(1,3,1,2.5),(2,1,1,10.0),(3,1,2,10.0);
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


COLS = ["name", "n_orders", "revenue"]


def test_example():
    check(QUERY, A, [("Asha", 2, 90.0), ("Bala", 1, 48.0), ("Chitra", 1, 78.0), ("Dev", 1, 15.0)],
          "n_orders must count ORDERS, not joined rows: Asha's order 101 has two lines, so COUNT(*) counts it twice. Count DISTINCT order ids. Keep the revenue as it is.",
          cols=COLS)


def test_same_book_in_two_orders():
    # Amy bought book 1 in two different orders: counting distinct books would give 1.
    check(QUERY, B, [("Amy", 2, 30.0), ("Zed", 1, 22.5)],
          "Amy has 2 orders that contain the same book. Count distinct ORDER ids (o.order_id), not books. Max has no orders and must not appear.",
          cols=COLS)
