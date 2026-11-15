import sqlite3
import pytest
from solution import QUERY

SCHEMA_A = """
CREATE TABLE authors (
  author_id INTEGER PRIMARY KEY,
  name      TEXT NOT NULL,
  country   TEXT
);
INSERT INTO authors VALUES
 (1, 'Mira Das',  'India'),
 (2, 'Tom Hale',  'UK'),
 (3, 'Lena Voss', 'Germany'),
 (4, 'Omar Reed', 'UK'),
 (5, 'Zed Park',  'Japan');
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
CREATE TABLE authors (
  author_id INTEGER PRIMARY KEY,
  name      TEXT NOT NULL,
  country   TEXT
);
INSERT INTO authors VALUES
 (1, 'Ann', 'UK'),
 (2, 'Bo',  'India'),
 (3, 'Cy',  'UK'),
 (4, 'Di',  'France');
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



def test_columns():
    assert colnames(connect(SCHEMA_A), QUERY) == ["author", "title"], "Columns: author, title."


def test_uses_left_join():
    assert "LEFT" in QUERY.upper() or "RIGHT" in QUERY.upper(), "Use an outer join that keeps all authors: LEFT JOIN with authors on the left."


def test_dataset_a():
    exp = [("Mira Das", "Quiet Rivers"), ("Mira Das", "Iron Garden"), ("Tom Hale", "Data Basics"),
           ("Tom Hale", "SQL in Practice"), ("Lena Voss", "Cooking Light"), ("Lena Voss", "Salt and Stone"),
           ("Omar Reed", "Night Train"), ("Omar Reed", "Paper Moons"), ("Zed Park", None)]
    assert same(rows(connect(SCHEMA_A), QUERY), exp), \
        "Zed Park has no books but must appear once with title NULL. Is authors on the LEFT side of LEFT JOIN?"


def test_dataset_b():
    exp = [("Ann", "Alpha"), ("Ann", "Beta"), ("Bo", "Gamma"), ("Bo", "Delta"), ("Cy", "Epsilon"),
           ("Cy", "Sigma Book"), ("Di", None)]
    assert same(rows(connect(SCHEMA_B), QUERY), exp), \
        "Dataset B: Di has no books (keep, with NULL). Omega has no author and is NOT part of this result (it is on the right side)."
