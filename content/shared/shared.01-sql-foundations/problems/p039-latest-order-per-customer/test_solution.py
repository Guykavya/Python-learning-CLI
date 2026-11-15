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
"""

B = """
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
INSERT INTO customers VALUES (1,'Zed','X'),(2,'Amy','Y'),(3,'Max','Z');
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES (1,1,'2024-05-01','shipped'),(2,1,'2024-05-01','shipped'),(3,1,'2024-04-01','shipped'),(4,2,'2024-06-09','pending');
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


COLS = ["name", "order_id", "ordered"]


def test_example():
    check(QUERY, A, [("Asha", 102, "2024-02-10"), ("Bala", 104, "2024-03-01"), ("Chitra", 105, "2024-03-15"), ("Dev", 103, "2024-02-11")],
          "One row per customer with orders: their newest order. Dev's only order (103) counts regardless of its status.", cols=COLS)


def test_ties_and_no_orders():
    check(QUERY, B, [("Amy", 4, "2024-06-09"), ("Zed", 2, "2024-05-01")],
          "Zed has orders 1 and 2 on the same latest date: return only order 2 (larger id). Max has no orders and must not appear.", cols=COLS)


def test_uses_subquery():
    assert QUERY.upper().count("SELECT") >= 2, "Use a correlated subquery (a SELECT inside the WHERE) for this exercise."
