import sqlite3

import pytest

from solution import QUERY

A = """
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, author_id INTEGER, price REAL);
INSERT INTO books VALUES (1,'Dune',1,10.0),(2,'Emma',2,6.0),(3,'SQL Basics',3,30.0),(4,'Python Deep',3,40.0),(5,'Cooking',4,15.0),(6,'Poems',2,7.0),(7,'Notes',3,12.0);
"""

B = """
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, author_id INTEGER, price REAL);
INSERT INTO books VALUES (1,'a',1,1.0),(2,'b',1,1.0),(3,'c',2,1.0),(4,'d',2,1.0),(5,'e',3,1.0),(6,'f',4,1.0),(7,'g',4,1.0),(8,'h',4,1.0),(9,'i',4,1.0);
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


COLS = ["author_id", "n_books"]


def test_example():
    check(QUERY, A, [(3, 3), (2, 2)],
          "Authors 3 (3 books) and 2 (2 books) qualify; authors 1 and 4 have only one. Use HAVING COUNT(*) >= 2.", cols=COLS)


def test_ties_and_boundary():
    check(QUERY, B, [(4, 4), (1, 2), (2, 2)],
          "Author 4 has 4 books; authors 1 and 2 tie on 2 books, so author_id decides. A count of exactly 2 must be kept (>= 2, not > 2).", cols=COLS)
