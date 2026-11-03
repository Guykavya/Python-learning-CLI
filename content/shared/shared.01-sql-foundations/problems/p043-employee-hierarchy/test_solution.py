import sqlite3

import pytest

from solution import QUERY

A = """
CREATE TABLE employees (emp_id INTEGER PRIMARY KEY, name TEXT NOT NULL, manager_id INTEGER REFERENCES employees(emp_id));
INSERT INTO employees VALUES (1,'Ria',NULL),(2,'Sam',1),(3,'Tia',1),(4,'Uma',2),(5,'Vik',2),(6,'Wen',4),(7,'Xan',3);
"""

B = """
CREATE TABLE employees (emp_id INTEGER PRIMARY KEY, name TEXT NOT NULL, manager_id INTEGER REFERENCES employees(emp_id));
INSERT INTO employees VALUES (1,'A',NULL),(2,'B',1),(3,'C',NULL),(4,'D',3),(5,'E',4),(6,'F',5),(7,'G',6);
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


COLS = ["emp_id", "name", "depth"]


def test_example():
    check(QUERY, A, [(1, "Ria", 0), (2, "Sam", 1), (3, "Tia", 1), (4, "Uma", 2), (5, "Vik", 2), (7, "Xan", 2), (6, "Wen", 3)],
          "Top person depth 0, each level adds 1. Wen reports to Uma who reports to Sam who reports to Ria: depth 3.", cols=COLS)


def test_two_roots_and_deep_chain():
    check(QUERY, B, [(1, "A", 0), (3, "C", 0), (2, "B", 1), (4, "D", 1), (5, "E", 2), (6, "F", 3), (7, "G", 4)],
          "There are two top-level people (A and C) and a chain of depth 4 (C -> D -> E -> F -> G). A fixed number of self joins cannot reach G.",
          cols=COLS)


def test_uses_recursion():
    assert "RECURSIVE" in QUERY.upper(), "Use WITH RECURSIVE."
