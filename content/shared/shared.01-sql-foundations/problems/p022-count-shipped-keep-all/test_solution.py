import sqlite3
import pytest
from solution import QUERY

SCHEMA_A = """
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  status      TEXT NOT NULL      -- 'shipped', 'pending' or 'cancelled'
);
INSERT INTO customers VALUES (1, 'Asha'), (2, 'Ben'), (3, 'Chen'), (4, 'Dia'), (5, 'Eli');
INSERT INTO orders VALUES (20, 1, 'shipped'), (21, 1, 'shipped'), (22, 1, 'pending'),
                          (23, 2, 'pending'), (24, 3, 'shipped'), (25, 5, 'cancelled');
"""

SCHEMA_B = """
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  status      TEXT NOT NULL      -- 'shipped', 'pending' or 'cancelled'
);
INSERT INTO customers VALUES (1, 'Pia'), (2, 'Quin'), (3, 'Rae');
INSERT INTO orders VALUES (1, 1, 'shipped'), (2, 1, 'shipped'), (3, 1, 'shipped'), (4, 2, 'cancelled');
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



def test_columns():
    assert colnames(connect(SCHEMA_A), QUERY) == ["name", "shipped_orders"], "Columns: name, shipped_orders."


def test_dataset_a():
    exp = [("Asha", 2), ("Ben", 0), ("Chen", 1), ("Dia", 0), ("Eli", 0)]
    assert same(rows(connect(SCHEMA_A), QUERY), exp), \
        "Expected every customer with the count of shipped orders. Missing customers? the status test belongs in ON, not WHERE. A 1 where you expect 0? use COUNT(o.order_id), not COUNT(*)."


def test_dataset_b():
    exp = [("Pia", 3), ("Quin", 0), ("Rae", 0)]
    assert same(rows(connect(SCHEMA_B), QUERY), exp), \
        "Dataset B: Quin has only a cancelled order and Rae has none: both must show 0."
