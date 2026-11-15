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

A = """CREATE TABLE monthly_sales (month TEXT, revenue INTEGER);
INSERT INTO monthly_sales VALUES ('2024-01',100),('2024-02',120),('2024-03',90),('2024-04',90);"""
B = """CREATE TABLE monthly_sales (month TEXT, revenue INTEGER);
INSERT INTO monthly_sales VALUES ('2024-03',50),('2024-01',80),('2024-02',80);"""
C = """CREATE TABLE monthly_sales (month TEXT, revenue INTEGER);
INSERT INTO monthly_sales VALUES ('2024-05',70);"""


def test_columns():
    cols = [d[0] for d in connect(A).execute(QUERY).description]
    assert cols == ["month", "revenue", "change"], f"Columns must be month, revenue, change. You returned {cols}."


def test_dataset_a():
    assert rows(connect(A), QUERY) == [("2024-01", 100, None), ("2024-02", 120, 20), ("2024-03", 90, -30), ("2024-04", 90, 0)], \
        "change = this month minus the previous month; the first month must be NULL (not 0)."


def test_unsorted_input():
    assert rows(connect(B), QUERY) == [("2024-01", 80, None), ("2024-02", 80, 0), ("2024-03", 50, -30)], \
        "Months were inserted out of order. LAG must use ORDER BY month inside OVER."


def test_single_row():
    assert rows(connect(C), QUERY) == [("2024-05", 70, None)], "One month only: change must be NULL."
