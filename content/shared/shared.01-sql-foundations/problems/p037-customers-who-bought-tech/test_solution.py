import sqlite3

import pytest

from solution import QUERY

A = """
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
INSERT INTO customers VALUES (1,'Asha','Pune'),(2,'Bala','Delhi'),(3,'Chitra',NULL),(4,'Dev','Pune');
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, category TEXT, price REAL NOT NULL);
INSERT INTO books VALUES
 (1,'Dune','fiction',10.0),(2,'Emma','fiction',6.0),(3,'SQL Basics','tech',30.0),
 (4,'Python Deep','tech',40.0),(5,'Cooking','food',15.0),(6,'Algorithms','tech',50.0);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES
 (101,1,'2024-01-05','shipped'),(102,1,'2024-02-10','shipped'),(103,4,'2024-02-11','cancelled'),
 (104,2,'2024-03-01','shipped'),(105,3,'2024-03-15','shipped');
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES
 (101,1,2,10.0),(101,3,1,30.0),(102,4,1,40.0),(103,5,1,15.0),
 (104,2,3,6.0),(104,3,1,30.0),(105,6,1,50.0),(105,3,1,28.0);
"""

B = """
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
INSERT INTO customers VALUES (1,'Zed','X'),(2,'Amy','Y'),(3,'Max','Z');
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, category TEXT, price REAL NOT NULL);
INSERT INTO books VALUES (1,'x','tech',10.0),(2,'y','tech',20.0),(3,'z','food',5.0);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES (1,1,'2024-01-01','shipped'),(2,1,'2024-01-02','shipped'),(3,2,'2024-01-03','shipped'),(4,3,'2024-01-04','shipped');
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES (1,1,1,10.0),(1,2,1,20.0),(2,1,1,10.0),(3,3,1,5.0),(3,2,1,20.0),(4,3,2,5.0);
"""


def connect(schema):
    con = sqlite3.connect(":memory:")
    con.executescript(schema)
    return con


def run(con, sql):
    """Run ONE query. Return (column names, rows). Fail clearly if SQLite rejects it."""
    try:
        cur = con.execute(sql)
    except (sqlite3.Error, sqlite3.Warning) as e:
        pytest.fail(f"SQLite rejected your query: {e}. Write exactly one statement, no trailing second statement.")
    if cur.description is None:
        pytest.fail("Your query returned no result set. Write a SELECT (or WITH ... SELECT).")
    return [d[0] for d in cur.description], cur.fetchall()


def check(sql, schema, want, msg, ordered=True, cols=None):
    con = connect(schema)
    names, got = run(con, sql)
    if cols is not None:
        assert names == cols, f"Column names/order must be {cols}, you returned {names}. Use AS to name them."
    if not ordered:
        got, want = sorted(got, key=repr), sorted(want, key=repr)
    assert got == want, f"{msg} Expected {want} but got {got}."


COLS = ["name"]


def test_example():
    check(QUERY, A, [("Asha",), ("Bala",), ("Chitra",)],
          "Asha, Bala and Chitra each bought a tech book. Dev only bought food. Each name once.", cols=COLS)


def test_no_duplicates_and_non_buyers():
    check(QUERY, B, [("Amy",), ("Zed",)],
          "Zed bought two tech books in the same order and again in another: his name must appear once. Max bought only food. Did you forget DISTINCT/IN?",
          cols=COLS)


def test_uses_in():
    assert " IN " in QUERY.upper().replace("\n", " "), "This exercise is about IN (SELECT ...)."
