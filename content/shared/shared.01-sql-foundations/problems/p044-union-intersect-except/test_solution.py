import sqlite3

import pytest

from solution import QUERY_A, QUERY_B, QUERY_C

A = """
CREATE TABLE newsletter (email TEXT);
CREATE TABLE buyers (email TEXT);
INSERT INTO newsletter VALUES ('a@x'),('b@x'),('c@x'),('b@x');
INSERT INTO buyers VALUES ('b@x'),('d@x'),('d@x');
"""

B = """
CREATE TABLE newsletter (email TEXT);
CREATE TABLE buyers (email TEXT);
INSERT INTO newsletter VALUES ('x@x'),('x@x'),('y@x');
INSERT INTO buyers VALUES ('y@x'),('z@x');
"""

C = """
CREATE TABLE newsletter (email TEXT);
CREATE TABLE buyers (email TEXT);
INSERT INTO newsletter VALUES ('p@x');
INSERT INTO buyers VALUES ('q@x');
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


def E(*xs):
    return [(x + "@x",) for x in xs]


def test_union():
    check(QUERY_A, A, E("a", "b", "c", "d"), "UNION: everyone on either list, each once, sorted. 'b' is on both lists and 'd' twice in buyers.", cols=["email"])
    check(QUERY_A, B, E("x", "y", "z"), "UNION removes duplicates: 'x' is twice on the newsletter.", cols=["email"])


def test_intersect():
    check(QUERY_B, A, E("b"), "INTERSECT: only 'b' is on both lists (once, although it is listed twice).", cols=["email"])
    check(QUERY_B, B, E("y"), "INTERSECT: only 'y' is on both lists.", cols=["email"])
    check(QUERY_B, C, [], "INTERSECT of two disjoint lists is empty.", cols=["email"])


def test_except():
    check(QUERY_C, A, E("a", "c"), "EXCEPT: newsletter MINUS buyers = a and c. Is your order of the two SELECTs right?", cols=["email"])
    check(QUERY_C, B, E("x"), "EXCEPT removes duplicates too: 'x' listed twice appears once.", cols=["email"])
    check(QUERY_C, C, E("p"), "No overlap: the newsletter address stays.", cols=["email"])


def test_keywords():
    assert "UNION" in QUERY_A.upper() and "ALL" not in QUERY_A.upper(), "QUERY_A must use UNION (not UNION ALL)."
    assert "INTERSECT" in QUERY_B.upper(), "QUERY_B must use INTERSECT."
    assert "EXCEPT" in QUERY_C.upper(), "QUERY_C must use EXCEPT."
