import ast
import inspect
import sqlite3

import pytest

import solution
from solution import add_customer, find_customer, books_between

SCHEMA = """CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, category TEXT, price REAL);
INSERT INTO books VALUES (1,'Rust Basics','Tech',30),(2,'Go Tour','Tech',20),(3,'Tales','Fiction',20),(4,'Epic','Fiction',30),(5,'Atlas','Maps',45.5);"""


@pytest.fixture()
def con():
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA)
    return c


def test_add_returns_id_and_commits(tmp_path):
    path = str(tmp_path / "s.db")
    c = sqlite3.connect(path)
    c.executescript(SCHEMA)
    first = add_customer(c, "Ada", "Pune")
    second = add_customer(c, "Bo", None)
    assert (first, second) == (1, 2), f"add_customer must return the new customer_id (cursor.lastrowid); got {first}, {second}."
    other = sqlite3.connect(path)
    assert other.execute("SELECT name, city FROM customers ORDER BY customer_id").fetchall() == [("Ada", "Pune"), ("Bo", None)], \
        "Rows must be committed (con.commit()) and a None city must be stored as NULL."


def test_apostrophe_and_sql_in_values(con):
    nasty = "Robert'); DROP TABLE customers;--"
    add_customer(con, "O'Brien", "Cork")
    add_customer(con, nasty, None)
    assert find_customer(con, "O'Brien") == (1, "O'Brien", "Cork"), "Values with quotes must work: pass them as parameters."
    assert find_customer(con, nasty) == (2, nasty, None)
    assert con.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 2, "The customers table must survive."


def test_find_returns_none_and_is_not_injectable(con):
    add_customer(con, "Ada", "Pune")
    assert find_customer(con, "Nobody") is None, "No match: return None (fetchone() does that; fetchall() would give [])."
    assert find_customer(con, "x' OR '1'='1") is None, "This string is just a name that does not exist. If you got a row, you pasted it into the SQL."


def test_find_lowest_id_first(con):
    add_customer(con, "Ada", "Pune")
    add_customer(con, "Ada", "Oslo")
    assert find_customer(con, "Ada") == (1, "Ada", "Pune"), "With duplicates, return the lowest customer_id."


def test_books_between(con):
    assert books_between(con, 20, 30) == ["Go Tour", "Tales", "Epic", "Rust Basics"], \
        "BETWEEN is inclusive; order by price, then title."
    assert books_between(con, 20, 30, "Tech") == ["Go Tour", "Rust Basics"], "Filter by category when it is given."
    assert books_between(con, 0, 100, category="Maps") == ["Atlas"]
    assert books_between(con, 31, 40) == [], "No books in range: empty list."
    assert books_between(con, 0, 100, None) == ["Go Tour", "Tales", "Epic", "Rust Basics", "Atlas"], \
        "category=None means every category (use :category IS NULL OR ...)."


def test_no_string_formatting_in_sql():
    tree = ast.parse(inspect.getsource(solution))
    bad = [n for n in ast.walk(tree) if isinstance(n, ast.JoinedStr)
           or (isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod) and isinstance(n.left, ast.Constant) and isinstance(n.left.value, str))
           or (isinstance(n, ast.Attribute) and n.attr == "format")]
    assert not bad, "Do not build SQL with f-strings, % or .format. Use ? / :name placeholders."
