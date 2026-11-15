import sqlite3
import pytest
from solution import QUERY

SCHEMA_A = """
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  city        TEXT,            -- NULL when unknown
  joined      TEXT NOT NULL    -- 'YYYY-MM-DD'
);
INSERT INTO customers VALUES
 (1, 'Asha', 'Pune',  '2023-01-10'),
 (2, 'Ben',  NULL,    '2023-02-03'),
 (3, 'Chen', 'Delhi', '2023-02-20'),
 (4, 'Dia',  NULL,    '2023-04-01'),
 (5, 'Eli',  'Pune',  '2023-05-12'),
 (6, 'Fay',  'Goa',   '2023-06-30');
"""

SCHEMA_B = """
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  city        TEXT,            -- NULL when unknown
  joined      TEXT NOT NULL    -- 'YYYY-MM-DD'
);
INSERT INTO customers VALUES
 (1, 'Pia',  'Pune', '2023-01-10'),
 (2, 'Quin', 'Oslo', '2023-02-03'),
 (3, 'Rae',  NULL,   '2023-02-20'),
 (4, 'Sam',  'Pune', '2023-04-01');
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
    exp = [("Ben",), ("Chen",), ("Dia",), ("Fay",)]
    assert same(rows(connect(SCHEMA_A), QUERY), exp), \
        "Expected 4 names: Ben, Chen, Dia, Fay. `city <> 'Pune'` alone drops the NULL cities (Ben, Dia): add `OR city IS NULL`."


def test_dataset_b():
    assert same(rows(connect(SCHEMA_B), QUERY), [("Quin",), ("Rae",)]), \
        "Dataset B: Quin (Oslo) and Rae (NULL). Pune customers must not appear."


def test_one_column():
    assert colnames(connect(SCHEMA_A), QUERY) == ["name"], "Return one column named name."
