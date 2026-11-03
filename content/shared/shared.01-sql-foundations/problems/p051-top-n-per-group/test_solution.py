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
 (1,'Asha','Eng',90),(2,'Ben','Eng',80),(3,'Chen','Ops',80),(4,'Dina','Ops',70),(5,'Eli','Eng',60),(6,'Fay','Ops',70);"""
B = """CREATE TABLE employees (emp_id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER);
INSERT INTO employees VALUES
 (7,'Hal','Ops',50),(8,'Ivy','Ops',50),(9,'Jo','Ops',50),(10,'Kim','Eng',100),(11,'Lee','Eng',100),
 (12,'Max','Eng',90),(13,'Gus','HR',55);"""


def test_columns():
    cols = [d[0] for d in connect(A).execute(QUERY).description]
    assert cols == ["dept", "name", "salary"], f"Columns must be dept, name, salary. You returned {cols}."


def test_dataset_a():
    assert rows(connect(A), QUERY) == [("Eng", "Asha", 90), ("Eng", "Ben", 80), ("Ops", "Chen", 80), ("Ops", "Dina", 70)], \
        "Expected the 2 best paid per department, ties broken by lower emp_id (Dina beats Fay)."


def test_dataset_b_ties_and_small_group():
    assert rows(connect(B), QUERY) == [
        ("Eng", "Kim", 100), ("Eng", "Lee", 100), ("HR", "Gus", 55), ("Ops", "Hal", 50), ("Ops", "Ivy", 50)], \
        "Eng has two people tied at 100, Ops has three tied at 50 (only 2 may appear, lowest emp_id first), HR has one person. RANK returns 3 Ops rows; LIMIT 2 returns only 2 rows in total."
