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
INSERT INTO customers VALUES (1,'Zed','X'),(2,'Amy','Y'),(3,'Max','Z'),(4,'Nil','Q'),(5,'Una','R'),(6,'Vic','S'),(7,'Wen','T');
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES (1,1,'2024-01-01','shipped'),(2,1,'2024-01-02','shipped'),(3,2,'2024-01-03','shipped'),(4,2,'2024-01-04','shipped'),(5,3,'2024-01-05','shipped'),(6,4,'2024-01-06','shipped'),(7,5,'2024-01-07','shipped'),(8,6,'2024-01-08','shipped');
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES (1,1,1,8.0),(2,1,1,12.0),(3,1,1,15.0),(4,1,1,25.0),(5,1,1,30.0),(6,1,1,30.0),(7,1,1,21.0),(8,1,1,19.0);
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


import re

COLS = ["name", "n_orders", "spent", "avg_order"]


def test_example():
    check(QUERY, A, [("Chitra", 1, 78.0, 78.0), ("Bala", 1, 48.0, 48.0)],
          "All orders average 46.2. Asha (avg 45.0) is below it, Dev (15.0) too. Compare to the average of ORDER totals, not of customers.", cols=COLS)


def test_boundary_and_multiple_orders():
    # order totals 8,12,15,25,30,30,21,19 -> overall exactly 20.0; customer averages 10,20,30,30,21,19
    check(QUERY, B, [("Max", 1, 30.0, 30.0), ("Nil", 1, 30.0, 30.0), ("Una", 1, 21.0, 21.0)],
          "The average of all 8 order totals is exactly 20.0. Amy's average is exactly 20.0 (not ABOVE it). Una (21.0) is above it: do not compare with the average of the customers' averages (21.67). Wen has no orders.", cols=COLS)


def test_layers():
    assert len(re.findall(r"\bAS\s*\(", QUERY.upper())) >= 2, "Use at least two chained CTEs (order_totals, customer_stats)."
