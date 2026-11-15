import sqlite3

import pytest

from solution import QUERY_A, QUERY_B

A = """
CREATE TABLE employees (emp_id INTEGER PRIMARY KEY, name TEXT NOT NULL, dept TEXT NOT NULL, salary INTEGER NOT NULL);
INSERT INTO employees VALUES (1,'Ann','Eng',100),(2,'Bob','Eng',90),(3,'Cy','Eng',90),(4,'Dee','Eng',80),(5,'Eli','Ops',70),(6,'Fay','Ops',60),(7,'Gus','Hr',50);
"""

B = """
CREATE TABLE employees (emp_id INTEGER PRIMARY KEY, name TEXT NOT NULL, dept TEXT NOT NULL, salary INTEGER NOT NULL);
INSERT INTO employees VALUES (1,'P','Dev',70),(2,'Q','Dev',70),(3,'R','Dev',70),(4,'S','Ops',60),(5,'T','Ops',40),(6,'U','Ops',60);
"""

C = """
CREATE TABLE employees (emp_id INTEGER PRIMARY KEY, name TEXT NOT NULL, dept TEXT NOT NULL, salary INTEGER NOT NULL);
INSERT INTO employees VALUES (1,'Solo','Dev',50),(2,'Twin','Ops',50);
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


def test_a_example():
    check(QUERY_A, A, [(90,)], "Distinct salaries from the top: 100, 90, 80 ... the second is 90.", cols=["second_highest"])


def test_a_ties_at_the_top():
    check(QUERY_A, B, [(60,)],
          "Salaries 70, 70, 70, 60, 40: the second DISTINCT value is 60. Without DISTINCT you would get 70.", cols=["second_highest"])


def test_a_no_second_value():
    check(QUERY_A, C, [(None,)],
          "All salaries are 50: there is no second value, but the result must still be ONE row containing NULL.", cols=["second_highest"])


COLS_B = ["dept", "name", "salary"]


def test_b_example():
    check(QUERY_B, A, [("Eng", "Bob", 90), ("Eng", "Cy", 90), ("Ops", "Fay", 60)],
          "Eng: distinct salaries 100, 90, 80 -> second is 90, earned by both Bob and Cy. Ops: Fay. Hr has one salary, so nobody.", cols=COLS_B)


def test_b_other_data():
    check(QUERY_B, B, [("Ops", "T", 40)],
          "Dev: everyone earns 70, there is no second-highest distinct salary. Ops: 60, 60, 40 -> the second distinct is 40: T. (Counting higher EMPLOYEES instead of higher salaries would miss T.)", cols=COLS_B)


def test_b_no_second():
    check(QUERY_B, C, [], "Each department has only one salary: nothing qualifies.", cols=COLS_B)


def test_no_windows():
    for q in (QUERY_A, QUERY_B):
        assert not re.search(r"\bOVER\b", q.upper()), "Do not use window functions here; use LIMIT/OFFSET and a correlated COUNT(DISTINCT ...)."
