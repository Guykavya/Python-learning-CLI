import sqlite3
import pytest
from solution import QUERY_A, QUERY_B, QUERY_C

SCHEMA_A = """
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  city        TEXT,            -- NULL when unknown
  joined      TEXT NOT NULL    -- 'YYYY-MM-DD'
);
INSERT INTO customers VALUES
 (1, 'Asha', 'Pune', '2023-01-10'),
 (2, 'Ben',  NULL,   '2023-02-03'),
 (3, 'Chen', '',     '2023-02-20'),
 (4, 'Dia',  NULL,   '2023-04-01'),
 (5, 'Eli',  'Pune', '2023-05-12');
"""

SCHEMA_B = """
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  city        TEXT,            -- NULL when unknown
  joined      TEXT NOT NULL    -- 'YYYY-MM-DD'
);
INSERT INTO customers VALUES
 (1, 'Zoe', '',     '2023-01-10'),
 (2, 'Yan', 'Oslo', '2023-02-03'),
 (3, 'Xi',  NULL,   '2023-02-20'),
 (4, 'Wen', '',     '2023-04-01');
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



def test_column_names():
    for q in (QUERY_A, QUERY_B, QUERY_C):
        assert colnames(connect(SCHEMA_A), q) == ["name", "city"], "Columns must be name, city. Alias the expression `AS city`."


def test_a_default_for_null():
    exp = [("Asha", "Pune"), ("Ben", "unknown"), ("Chen", ""), ("Dia", "unknown"), ("Eli", "Pune")]
    assert same(rows(connect(SCHEMA_A), QUERY_A), exp), "QUERY_A: COALESCE only replaces NULL. Chen's empty string stays empty."
    exp = [("Zoe", ""), ("Yan", "Oslo"), ("Xi", "unknown"), ("Wen", "")]
    assert same(rows(connect(SCHEMA_B), QUERY_A), exp), "QUERY_A on dataset B."


def test_b_nullif():
    exp = [("Asha", "Pune"), ("Ben", None), ("Chen", None), ("Dia", None), ("Eli", "Pune")]
    assert same(rows(connect(SCHEMA_A), QUERY_B), exp), "QUERY_B: NULLIF(city, '') turns the empty string into NULL; real NULLs stay NULL."
    exp = [("Zoe", None), ("Yan", "Oslo"), ("Xi", None), ("Wen", None)]
    assert same(rows(connect(SCHEMA_B), QUERY_B), exp), "QUERY_B on dataset B."


def test_c_both():
    exp = [("Asha", "Pune"), ("Ben", "unknown"), ("Chen", "unknown"), ("Dia", "unknown"), ("Eli", "Pune")]
    assert same(rows(connect(SCHEMA_A), QUERY_C), exp), "QUERY_C: clean the empty string first (NULLIF), then default (COALESCE). Nest them."
    exp = [("Zoe", "unknown"), ("Yan", "Oslo"), ("Xi", "unknown"), ("Wen", "unknown")]
    assert same(rows(connect(SCHEMA_B), QUERY_C), exp), "QUERY_C on dataset B."
