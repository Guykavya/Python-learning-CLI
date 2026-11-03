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
INSERT INTO customers VALUES (1,'Zed','X'),(2,'Amy','Y'),(3,'Max','Z'),(4,'Nil','Z');
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES (1,1,'2024-01-01','shipped'),(2,2,'2024-01-02','shipped'),(3,2,'2024-01-03','pending'),(4,3,'2024-01-04','cancelled');
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES (1,1,1,10.0),(2,1,2,10.0),(2,2,1,5.5),(3,3,1,9.5),(4,1,5,10.0);
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


COLS = ["name", "revenue"]


def test_example():
    check(QUERY, A, [("Asha", 90.0), ("Chitra", 78.0), ("Bala", 48.0)],
          "Revenue = SUM(qty * unit_price) per customer over NON-cancelled orders. Dev has only a cancelled order and must not appear.", cols=COLS)


def test_other_data():
    # Amy: order 2 = 20 + 5.5 = 25.5 and order 3 (pending) = 9.5 -> 35.0 ; Zed = 10.0 ; Max only cancelled ; Nil no orders
    check(QUERY, B, [("Amy", 35.0), ("Zed", 10.0)],
          "Amy has a shipped and a pending order (both count: only 'cancelled' is excluded). Max has a cancelled order only; Nil has none.", cols=COLS)


def test_uses_join():
    assert "JOIN" in QUERY.upper(), "The point of this exercise is the JOIN of customers, orders and order_items."
