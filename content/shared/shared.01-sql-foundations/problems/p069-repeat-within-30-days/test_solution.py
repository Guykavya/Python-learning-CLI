import sqlite3
import pytest

from solution import QUERY


def connect(schema):
    con = sqlite3.connect(":memory:")
    con.executescript(schema)
    return con


def rows(con, sql):
    try:
        return con.execute(sql).fetchall()
    except sqlite3.Error as e:
        pytest.fail(f"SQLite rejected your query: {e}")

HEAD = """CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
"""
A = """CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO customers VALUES (1,'c1'),(2,'c2'),(3,'c3'),(4,'c4'),(5,'c5');
INSERT INTO orders VALUES
 (1,1,'2024-01-01','shipped'),(2,1,'2024-01-20','shipped'),
 (3,2,'2024-01-05','shipped'),(4,2,'2024-03-01','shipped'),(8,2,'2024-03-20','shipped'),
 (5,3,'2024-02-01','shipped'),
 (6,4,'2024-02-10','shipped'),(7,4,'2024-03-11','cancelled');"""
B = HEAD + """INSERT INTO customers VALUES (1,'c1'),(2,'c2'),(3,'c3'),(4,'c4'),(5,'c5'),(6,'c6'),(7,'c7'),(8,'c8');
INSERT INTO orders VALUES
 (1,1,'2024-05-01','shipped'),(2,1,'2024-05-01','shipped'),
 (3,2,'2024-05-01','shipped'),(4,2,'2024-05-31','shipped'),
 (5,3,'2024-05-01','shipped'),(6,3,'2024-06-01','shipped'),
 (7,4,'2024-05-01','shipped'),
 (8,5,'2024-05-01','shipped'),(9,5,'2024-05-02','shipped'),(10,5,'2024-05-03','shipped'),
 (20,6,'2024-06-10','shipped'),(21,6,'2024-06-01','shipped'),
 (30,7,'2024-07-04','shipped');"""
C = HEAD + "INSERT INTO customers VALUES (1,'c1');"


def test_columns():
    cols = [d[0] for d in connect(A).execute(QUERY).description]
    assert cols == ["customers", "repeaters", "pct_repeat"], f"Columns must be customers, repeaters, pct_repeat. You returned {cols}."


def test_dataset_a():
    assert rows(connect(A), QUERY) == [(4, 2, 50.0)], \
        "Expected 4 customers with orders and 2 repeaters (c1: day 19; c4: exactly day 30). c2's later orders are 56 and 75 days after the FIRST order."


def test_dataset_b():
    assert rows(connect(B), QUERY) == [(7, 3, 42.9)], \
        "Expected (7, 3, 42.9). c1 ordered twice on the SAME day (not a repeater); c2 is at day 30 (counts); c3 is at day 31 (no); c5 has two follow-ups but counts once (a join without DISTINCT counts it twice); c6's first order is by DATE (order_id 21, 06-01), not the lowest id; c8 never ordered and is not in the base."


def test_nobody_ordered():
    assert rows(connect(C), QUERY) == [(0, 0, None)], "With no orders return (0, 0, NULL): guard the division with NULLIF(..., 0)."
