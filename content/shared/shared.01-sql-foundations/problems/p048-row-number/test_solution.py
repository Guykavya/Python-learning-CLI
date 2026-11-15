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
 (1,'Zed','Eng',50),(2,'Amy','Eng',50),(3,'Bo','Ops',70),(4,'Cy','Ops',50);"""


def test_columns_named():
    con = connect(A)
    cols = [d[0] for d in con.execute(QUERY).description]
    assert cols == ["name", "salary", "rn"], f"Columns must be name, salary, rn in that order, you returned {cols}."


def test_dataset_a():
    assert rows(connect(A), QUERY) == [("Asha", 90, 1), ("Ben", 80, 2), ("Chen", 80, 3), ("Dina", 70, 4), ("Eli", 60, 5)], \
        "Number by salary DESC with name as tie-break; the result must be ordered by rn."


def test_ties_broken_by_name():
    got = rows(connect(B), QUERY)
    assert got == [("Bo", 70, 1), ("Amy", 50, 2), ("Cy", 50, 3), ("Zed", 50, 4)], \
        "Three people earn 50. They must get 2, 3, 4 in name order (Amy, Cy, Zed). Is ROW_NUMBER missing the name tie-break? Did you use RANK (which repeats numbers)?"


def test_uses_window():
    assert "OVER" in QUERY.upper(), "Use a window function: ROW_NUMBER() OVER (...)."
