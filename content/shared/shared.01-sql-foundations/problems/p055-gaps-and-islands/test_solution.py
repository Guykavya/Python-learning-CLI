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

A = """CREATE TABLE activity (day TEXT PRIMARY KEY);
INSERT INTO activity VALUES ('2024-01-01'),('2024-01-02'),('2024-01-03'),('2024-01-05'),('2024-01-07'),('2024-01-08');"""
B = """CREATE TABLE activity (day TEXT PRIMARY KEY);
INSERT INTO activity VALUES ('2024-03-05'),('2024-02-28'),('2024-02-27'),('2024-03-01'),('2024-02-29'),
 ('2025-01-01'),('2024-12-31'),('2024-03-07');"""
C = """CREATE TABLE activity (day TEXT PRIMARY KEY);"""


def test_columns():
    cols = [d[0] for d in connect(A).execute(QUERY).description]
    assert cols == ["start_day", "end_day", "days"], f"Columns must be start_day, end_day, days. You returned {cols}."


def test_dataset_a():
    assert rows(connect(A), QUERY) == [("2024-01-01", "2024-01-03", 3), ("2024-01-05", "2024-01-05", 1), ("2024-01-07", "2024-01-08", 2)], \
        "Expected three streaks. A gap of one or more days starts a new streak; an isolated day is a streak of 1."


def test_month_year_boundaries_and_leap_day():
    assert rows(connect(B), QUERY) == [
        ("2024-02-27", "2024-03-01", 4), ("2024-03-05", "2024-03-05", 1), ("2024-03-07", "2024-03-07", 1), ("2024-12-31", "2025-01-01", 2)], \
        "27 Feb, 28 Feb, 29 Feb (leap year) and 1 Mar form ONE streak of 4; 31 Dec and 1 Jan too. Do not use day-of-month arithmetic; use date(day, '-N days') or julianday."


def test_empty_table():
    assert rows(connect(C), QUERY) == [], "No activity means no streaks (zero rows)."
