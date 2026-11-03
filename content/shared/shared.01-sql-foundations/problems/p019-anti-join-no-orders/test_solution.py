import sqlite3
import pytest
from solution import QUERY

SCHEMA_A = """
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  city        TEXT
);
CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER,          -- may be NULL for guest checkout
  ordered     TEXT NOT NULL
);
INSERT INTO customers VALUES
 (1, 'Asha', 'Pune'), (2, 'Ben', NULL), (3, 'Chen', 'Delhi'),
 (4, 'Dia', NULL), (5, 'Eli', 'Pune'), (6, 'Fay', 'Goa');
INSERT INTO orders VALUES
 (10, 1, '2024-01-05'), (11, 1, '2024-02-10'), (12, 2, '2024-02-11'),
 (13, 3, '2024-03-01'), (14, 5, '2024-03-15');
"""

SCHEMA_B = """
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  city        TEXT
);
CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER,          -- may be NULL for guest checkout
  ordered     TEXT NOT NULL
);
INSERT INTO customers VALUES (1, 'Pia', 'Pune'), (2, 'Quin', 'Oslo'), (3, 'Rae', NULL);
INSERT INTO orders VALUES (20, 1, '2024-01-01'), (21, 1, '2024-01-02'), (22, NULL, '2024-01-03');
"""


def connect(schema):
    con = sqlite3.connect(":memory:")
    con.executescript(schema)
    return con


def rows(con, sql):
    try:
        return con.execute(sql).fetchall()
    except sqlite3.Error as e:
        pytest.fail(f"SQLite rejected your query: {e}")


def colnames(con, sql):
    try:
        return [d[0] for d in con.execute(sql).description]
    except sqlite3.Error as e:
        pytest.fail(f"SQLite rejected your query: {e}")


def same(a, b):
    return sorted(a, key=repr) == sorted(b, key=repr)



def test_dataset_a():
    assert same(rows(connect(SCHEMA_A), QUERY), [("Dia",), ("Fay",)]), \
        "Customers 4 (Dia) and 6 (Fay) never ordered. Use LEFT JOIN and keep rows where the order side is NULL."


def test_dataset_b_null_customer_id_in_orders():
    assert same(rows(connect(SCHEMA_B), QUERY), [("Quin",), ("Rae",)]), \
        "Expected Quin and Rae. If you got nothing, you used NOT IN and the NULL customer_id in orders broke it."


def test_one_column():
    assert colnames(connect(SCHEMA_A), QUERY) == ["name"], "Return one column named name."
