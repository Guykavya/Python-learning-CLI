import sqlite3
import pytest

from solution import SCRIPT

BASE = """CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, category TEXT, price REAL);
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT, tier TEXT NOT NULL DEFAULT 'basic');
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
"""
A = BASE + """INSERT INTO books VALUES (1,'Rust Basics','Tech',30),(2,'Tales','Fiction',10),(3,'Go Tour','Tech',20);
INSERT INTO customers (customer_id, name) VALUES (1,'Ada'),(2,'Bo'),(3,'Cy');
INSERT INTO orders VALUES (1,1,'2024-01-01','shipped'),(2,1,'2024-02-01','shipped'),(3,2,'2024-02-05','shipped');"""
B = BASE + """INSERT INTO books VALUES (1,'A','Tech',9.99),(2,'B','tech',50),(3,'C','Maps',40),(4,'D','Tech',100);
INSERT INTO customers (customer_id, name) VALUES (1,'Di'),(2,'Eve'),(3,'Fay'),(4,'Gus');
INSERT INTO orders VALUES (1,2,'2024-01-01','shipped'),(2,2,'2024-01-02','cancelled'),(3,2,'2024-01-03','shipped'),
 (4,3,'2024-01-04','shipped'),(5,4,'2024-01-05','shipped'),(6,4,'2024-01-06','shipped');"""


def run(schema):
    con = sqlite3.connect(":memory:")
    con.executescript(schema)
    try:
        con.executescript(SCRIPT)
    except sqlite3.Error as e:
        pytest.fail(f"SQLite rejected your script: {e}")
    return con


def test_prices_a():
    con = run(A)
    got = con.execute("SELECT book_id, price FROM books ORDER BY book_id").fetchall()
    assert got == [(1, 33.0), (2, 10.0), (3, 22.0)], f"Only Tech books rise by 10 percent, rounded to 2 decimals. Got {got}. (No WHERE changes every book; no ROUND leaves 22.000000000000004.)"


def test_prices_b():
    con = run(B)
    got = con.execute("SELECT book_id, price FROM books ORDER BY book_id").fetchall()
    assert got == [(1, 10.99), (2, 50.0), (3, 40.0), (4, 110.0)], f"Category match is exact: 'Tech' only (not 'tech'). Round to 2 decimals. Got {got}."


def test_tiers_a():
    con = run(A)
    got = con.execute("SELECT customer_id, tier FROM customers ORDER BY customer_id").fetchall()
    assert got == [(1, "gold"), (2, "basic"), (3, "basic")], f"Only customers with 2 or more orders become gold. Got {got}."


def test_tiers_b():
    con = run(B)
    got = con.execute("SELECT customer_id, tier FROM customers ORDER BY customer_id").fetchall()
    assert got == [(1, "basic"), (2, "gold"), (3, "basic"), (4, "gold")], f"Cancelled orders still count as orders here (customer 2 has three). A customer with 0 or 1 orders stays basic. Got {got}."


def test_uses_subquery():
    s = SCRIPT.upper()
    assert s.count("UPDATE") >= 2 and "SELECT" in s, "Use two UPDATE statements; the second one needs a subquery."
