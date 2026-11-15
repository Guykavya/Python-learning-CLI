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

A = """CREATE TABLE daily_sales (day TEXT, store TEXT, amount REAL);
INSERT INTO daily_sales VALUES
 ('2024-01-01','A',10),('2024-01-02','A',20),('2024-01-03','A',5),
 ('2024-01-01','B',7),('2024-01-03','B',3);"""
B = """CREATE TABLE daily_sales (day TEXT, store TEXT, amount REAL);
INSERT INTO daily_sales VALUES
 ('2024-02-03','N',4),('2024-02-01','N',-6),('2024-02-02','N',10),
 ('2024-02-05','S',100),('2024-02-01','E',2.5);"""


def test_columns():
    cols = [d[0] for d in connect(A).execute(QUERY).description]
    assert cols == ["store", "day", "amount", "running"], f"Columns must be store, day, amount, running. You returned {cols}."


def test_dataset_a():
    assert rows(connect(A), QUERY) == [
        ("A", "2024-01-01", 10, 10), ("A", "2024-01-02", 20, 30), ("A", "2024-01-03", 5, 35),
        ("B", "2024-01-01", 7, 7), ("B", "2024-01-03", 3, 10)], \
        "Running total restarts for each store. If B starts at 45 you forgot PARTITION BY store; if every row shows 35 you forgot ORDER BY inside OVER."


def test_dataset_b_unsorted_input_and_negative():
    assert rows(connect(B), QUERY) == [
        ("E", "2024-02-01", 2.5, 2.5),
        ("N", "2024-02-01", -6, -6), ("N", "2024-02-02", 10, 4), ("N", "2024-02-03", 4, 8),
        ("S", "2024-02-05", 100, 100)], \
        "Rows were inserted out of date order. The running total must follow the day order (ORDER BY day inside OVER), not insertion order."
