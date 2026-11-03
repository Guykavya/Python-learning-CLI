import sqlite3
import pytest
from solution import QUERY

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

SCHEMA_C = """
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
 (1, 'Zeta',  1, 'fiction', 15.50, '2020-01-01', 10),
 (2, 'Beta',  1, 'fiction', 15.50, '2020-01-02', 10),
 (3, 'Mu',    1, 'fiction', 15.50, '2020-01-03', 10);
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
    con = connect(SCHEMA_A)
    assert colnames(con, QUERY) == ["category", "title", "price"], "Columns: category, title, price in that order."


def test_dataset_a_exact_order():
    con = connect(SCHEMA_A)
    expected = [("cooking", "Cooking Light", 18.0), ("cooking", "Salt and Stone", 18.0),
                ("fiction", "Paper Moons", 14.25), ("fiction", "Quiet Rivers", 12.5),
                ("fiction", "Iron Garden", 9.99), ("mystery", "Night Train", 9.99),
                ("tech", "SQL in Practice", 45.5), ("tech", "Data Basics", 39.0)]
    assert rows(con, QUERY) == expected, \
        "Wrong order. Category A-Z, then price DESC, then title A-Z. Both cooking books cost 18.00: title decides."


def test_dataset_b_exact_order():
    con = connect(SCHEMA_B)
    expected = [("cooking", "Epsilon", 5.0), ("fiction", "Beta", 20.0), ("fiction", "Sigma Book", 15.5),
                ("fiction", "Alpha", 10.0), ("mystery", "Omega", 9.99), ("tech", "Gamma", 20.0),
                ("tech", "Delta", 5.0)]
    assert rows(con, QUERY) == expected, \
        "Check where DESC applies: it belongs only to price, not to category or title."


def test_dataset_c_ties_use_title():
    con = connect(SCHEMA_C)
    assert rows(con, QUERY) == [("fiction", "Beta", 15.5), ("fiction", "Mu", 15.5), ("fiction", "Zeta", 15.5)], \
        "Three books with the same category and price: the third key (title A-Z) must decide the order."
