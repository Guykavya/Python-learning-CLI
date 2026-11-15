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

A = """CREATE TABLE employees (emp_id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER);
INSERT INTO employees VALUES
 (1,'Asha','Eng',90),(2,'Ben','Eng',80),(3,'Chen','Ops',80),(4,'Dina','Ops',70),(5,'Eli','Eng',60);"""
B = """CREATE TABLE employees (emp_id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER);
INSERT INTO employees VALUES
 (1,'Zed',  'Eng',50),(2,'Amy','Eng',50),(3,'Bo','Ops',70),(4,'Cy','Ops',50),(5,'Di','Ops',40);"""


def test_columns():
    cols = [d[0] for d in connect(A).execute(QUERY).description]
    assert cols == ["name", "salary", "rnk", "drnk"], f"Columns must be name, salary, rnk, drnk. You returned {cols}."


def test_dataset_a():
    assert rows(connect(A), QUERY) == [("Asha", 90, 1, 1), ("Ben", 80, 2, 2), ("Chen", 80, 2, 2), ("Dina", 70, 4, 3), ("Eli", 60, 5, 4)], \
        "Equal salaries must share a rank. RANK then skips (2,2,4); DENSE_RANK does not (2,2,3)."


def test_dataset_b_three_way_tie():
    assert rows(connect(B), QUERY) == [("Bo", 70, 1, 1), ("Amy", 50, 2, 2), ("Cy", 50, 2, 2), ("Zed", 50, 2, 2), ("Di", 40, 5, 3)], \
        "Three people tie at 50: RANK gives 2,2,2 and the next is 5; DENSE_RANK gives 2,2,2 and the next is 3. Did you add name to the window ORDER BY (that breaks the ties)?"


def test_uses_both_functions():
    q = QUERY.upper()
    assert "DENSE_RANK" in q and "RANK()" in q.replace("DENSE_RANK()", ""), "Use both RANK() and DENSE_RANK()."
