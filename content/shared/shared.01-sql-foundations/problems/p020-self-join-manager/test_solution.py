import sqlite3
import pytest
from solution import QUERY

SCHEMA_A = """
CREATE TABLE employees (
  emp_id     INTEGER PRIMARY KEY,
  name       TEXT NOT NULL,
  manager_id INTEGER REFERENCES employees(emp_id),   -- NULL for the top person
  dept       TEXT NOT NULL,
  salary     INTEGER NOT NULL
);
INSERT INTO employees VALUES
 (1, 'Meera', NULL, 'exec', 150000),
 (2, 'Ravi',  1,    'eng',  110000),
 (3, 'Sana',  1,    'ops',   95000),
 (4, 'Tej',   2,    'eng',   90000),
 (5, 'Uma',   2,    'eng',   92000),
 (6, 'Vik',   3,    'ops',   70000);
"""

SCHEMA_B = """
CREATE TABLE employees (
  emp_id     INTEGER PRIMARY KEY,
  name       TEXT NOT NULL,
  manager_id INTEGER REFERENCES employees(emp_id),   -- NULL for the top person
  dept       TEXT NOT NULL,
  salary     INTEGER NOT NULL
);
INSERT INTO employees VALUES
 (1, 'Ana', NULL, 'exec', 100),
 (2, 'Bo',  1,    'eng',   80),
 (3, 'Cy',  2,    'eng',   60),
 (4, 'Di',  NULL, 'ops',   90);
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
    assert colnames(connect(SCHEMA_A), QUERY) == ["employee", "manager"], "Columns: employee, manager."


def test_dataset_a():
    exp = [("Meera", None), ("Ravi", "Meera"), ("Sana", "Meera"), ("Tej", "Ravi"), ("Uma", "Ravi"), ("Vik", "Sana")]
    assert same(rows(connect(SCHEMA_A), QUERY), exp), \
        "6 rows expected. Meera has no manager and must still appear (LEFT JOIN). Match e.manager_id = m.emp_id."


def test_dataset_b_two_roots():
    exp = [("Ana", None), ("Bo", "Ana"), ("Cy", "Bo"), ("Di", None)]
    assert same(rows(connect(SCHEMA_B), QUERY), exp), "Two employees have no manager (Ana and Di): both must appear with NULL."
