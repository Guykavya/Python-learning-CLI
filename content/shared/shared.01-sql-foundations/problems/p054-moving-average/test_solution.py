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

A = """CREATE TABLE daily (day INTEGER, amount INTEGER);
INSERT INTO daily VALUES (1,10),(2,20),(3,35),(4,40),(5,50);"""
B = """CREATE TABLE daily (day INTEGER, amount INTEGER);
INSERT INTO daily VALUES (3,6),(1,4),(4,10),(2,8);"""


def test_columns():
    cols = [d[0] for d in connect(A).execute(QUERY).description]
    assert cols == ["day", "amount", "ma3"], f"Columns must be day, amount, ma3. You returned {cols}."


def test_dataset_a():
    got = rows(connect(A), QUERY)
    assert got == [(1, 10, 10.0), (2, 20, 15.0), (3, 35, 21.67), (4, 40, 31.67), (5, 50, 41.67)], \
        "Average of the current row and up to 2 rows before it, rounded to 2 decimals. Early rows use the rows that exist."


def test_dataset_b_unsorted():
    got = rows(connect(B), QUERY)
    assert got == [(1, 4, 4.0), (2, 8, 6.0), (3, 6, 6.0), (4, 10, 8.0)], \
        "Frame size is 3 rows: current + 2 before. Check ORDER BY day inside OVER, and ROWS BETWEEN 2 PRECEDING AND CURRENT ROW."


def test_uses_a_frame():
    assert "PRECEDING" in QUERY.upper(), "Use an explicit frame: ROWS BETWEEN 2 PRECEDING AND CURRENT ROW."
