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

A = """CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, category TEXT, price REAL);
INSERT INTO books VALUES (1,'Rust Basics','Tech',30),(2,'Go Tour','Tech',20),(3,'Tales','Fiction',10),(4,'Epic','Fiction',30),(5,'Atlas','Maps',40);"""
B = """CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, category TEXT, price REAL);
INSERT INTO books VALUES (1,'X','A',12.5),(2,'Y','A',37.5),(3,'Z','B',50);"""


def test_columns():
    cols = [d[0] for d in connect(A).execute(QUERY).description]
    assert cols == ["title", "category", "price", "pct_category", "pct_all"], f"Wrong column names or order: {cols}."


def test_dataset_a():
    assert rows(connect(A), QUERY) == [
        ("Rust Basics", "Tech", 30.0, 60.0, 23.1), ("Go Tour", "Tech", 20.0, 40.0, 15.4),
        ("Tales", "Fiction", 10.0, 25.0, 7.7), ("Epic", "Fiction", 30.0, 75.0, 23.1), ("Atlas", "Maps", 40.0, 100.0, 30.8)], \
        "pct_category = price / total of its category; pct_all = price / total of all books; round to 1 decimal. A 0 means integer division: use 100.0 * price."


def test_dataset_b():
    assert rows(connect(B), QUERY) == [("X", "A", 12.5, 25.0, 12.5), ("Y", "A", 37.5, 75.0, 37.5), ("Z", "B", 50.0, 100.0, 50.0)], \
        "A one-book category must show 100.0 for pct_category."


def test_uses_window():
    assert QUERY.upper().count("OVER") >= 2, "Use two window sums (SUM(price) OVER (...))."
