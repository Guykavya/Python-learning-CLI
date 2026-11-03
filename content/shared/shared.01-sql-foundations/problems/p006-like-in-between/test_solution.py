import sqlite3
import pytest
from solution import QUERY_A, QUERY_B, QUERY_C

SCHEMA_A = """
CREATE TABLE books (
  book_id   INTEGER PRIMARY KEY,
  title     TEXT NOT NULL,
  author_id INTEGER,
  category  TEXT NOT NULL,
  price     REAL NOT NULL,
  published TEXT NOT NULL,   -- 'YYYY-MM-DD'
  pages     INTEGER          -- NULL when unknown
);
INSERT INTO books VALUES
 (1, 'Quiet Rivers',    1, 'fiction', 12.50, '2019-03-10', 320),
 (2, 'Iron Garden',     1, 'fiction',  9.99, '2021-07-01', 280),
 (3, 'Data Basics',     2, 'tech',    39.00, '2020-01-15', 450),
 (4, 'SQL in Practice', 2, 'tech',    45.50, '2022-05-20', NULL),
 (5, 'Cooking Light',   3, 'cooking', 18.00, '2018-11-30', 200),
 (6, 'Salt and Stone',  3, 'cooking', 18.00, '2023-02-14', 240),
 (7, 'Night Train',     4, 'mystery',  9.99, '2022-09-09', 310),
 (8, 'Paper Moons',     4, 'fiction', 14.25, '2017-06-25', NULL);
"""

SCHEMA_B = """
CREATE TABLE books (
  book_id   INTEGER PRIMARY KEY,
  title     TEXT NOT NULL,
  author_id INTEGER,
  category  TEXT NOT NULL,
  price     REAL NOT NULL,
  published TEXT NOT NULL,   -- 'YYYY-MM-DD'
  pages     INTEGER          -- NULL when unknown
);
INSERT INTO books VALUES
 (1, 'Alpha',      1, 'fiction', 10.00, '2020-06-15', 100),
 (2, 'Beta',       1, 'fiction', 20.00, '2021-12-31', NULL),
 (3, 'Gamma',      2, 'tech',    20.00, '2022-01-01', 300),
 (4, 'Delta',      2, 'tech',     5.00, '2022-06-30', 50),
 (5, 'Epsilon',    3, 'cooking',  5.00, '2019-02-28', NULL),
 (6, 'Sigma Book', 3, 'fiction', 15.50, '2022-03-03', 120),
 (7, 'Omega',   NULL, 'mystery',  9.99, '2018-08-08', 90);
"""


def connect(schema):
    con = sqlite3.connect(":memory:")
    con.executescript(schema)
    return con


def rows(con, sql):
    try:
        return con.execute(sql).fetchall()
    except sqlite3.Error as e:
        pytest.fail(f"SQLite rejected your query: {e}")


def colnames(con, sql):
    try:
        return [d[0] for d in con.execute(sql).description]
    except sqlite3.Error as e:
        pytest.fail(f"SQLite rejected your query: {e}")


def same(a, b):
    return sorted(a, key=repr) == sorted(b, key=repr)



def titles(con, q):
    return [r[0] for r in rows(con, q)]


def test_a_like_prefix():
    assert sorted(titles(connect(SCHEMA_A), QUERY_A)) == ["SQL in Practice", "Salt and Stone"], \
        "QUERY_A: titles starting with S. Use LIKE 'S%' (the % goes AFTER the letter)."
    assert titles(connect(SCHEMA_B), QUERY_A) == ["Sigma Book"], "QUERY_A on dataset B: only Sigma Book starts with S."


def test_b_in():
    assert sorted(titles(connect(SCHEMA_A), QUERY_B)) == ["Cooking Light", "Data Basics", "SQL in Practice", "Salt and Stone"], \
        "QUERY_B: category tech or cooking."
    assert sorted(titles(connect(SCHEMA_B), QUERY_B)) == ["Delta", "Epsilon", "Gamma"], "QUERY_B on dataset B."
    assert "IN" in QUERY_B.upper().split("WHERE")[-1], "Use IN (...) in QUERY_B, as the statement asks."


def test_c_between_inclusive():
    assert sorted(titles(connect(SCHEMA_A), QUERY_C)) == ["Cooking Light", "Paper Moons", "Quiet Rivers", "Salt and Stone"], \
        "QUERY_C: 10 to 18. A price of exactly 18.00 is included."
    assert sorted(titles(connect(SCHEMA_B), QUERY_C)) == ["Alpha", "Sigma Book"], \
        "QUERY_C on dataset B: Alpha costs exactly 10.00 and must be included (BETWEEN is inclusive)."
    assert "BETWEEN" in QUERY_C.upper(), "Use BETWEEN in QUERY_C, as the statement asks."
