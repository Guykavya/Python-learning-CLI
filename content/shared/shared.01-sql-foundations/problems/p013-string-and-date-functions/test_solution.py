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



def test_a_names():
    assert colnames(connect(SCHEMA_A), QUERY_A) == ["title", "year", "short", "len"], "QUERY_A columns: title, year, short, len."


def test_a_values():
    exp = [("Quiet Rivers", "2019", "Qui", 12), ("Iron Garden", "2021", "Iro", 11), ("Data Basics", "2020", "Dat", 11),
           ("SQL in Practice", "2022", "SQL", 15), ("Cooking Light", "2018", "Coo", 13),
           ("Salt and Stone", "2023", "Sal", 14), ("Night Train", "2022", "Nig", 11), ("Paper Moons", "2017", "Pap", 11)]
    assert same(rows(connect(SCHEMA_A), QUERY_A), exp), \
        "year must be TEXT like '2019'; short = substr(title, 1, 3) (positions start at 1); len = length(title)."
    exp = [("Alpha", "2020", "Alp", 5), ("Beta", "2021", "Bet", 4), ("Gamma", "2022", "Gam", 5), ("Delta", "2022", "Del", 5),
           ("Epsilon", "2019", "Eps", 7), ("Sigma Book", "2022", "Sig", 10), ("Omega", "2018", "Ome", 5)]
    assert same(rows(connect(SCHEMA_B), QUERY_A), exp), "QUERY_A on dataset B."


def test_b_year_filter():
    assert same(rows(connect(SCHEMA_A), QUERY_B), [("SQL in Practice",), ("Night Train",)]), \
        "QUERY_B: published in 2022. Compare strftime('%Y', published) with the TEXT '2022'."
    assert same(rows(connect(SCHEMA_B), QUERY_B), [("Gamma",), ("Delta",), ("Sigma Book",)]), \
        "QUERY_B on dataset B: Gamma is published on 2022-01-01 and must be included."


def test_c_days():
    assert colnames(connect(SCHEMA_A), QUERY_C) == ["title", "days_old"], "QUERY_C columns: title, days_old."
    exp = [("Quiet Rivers", 1758), ("Iron Garden", 914), ("Data Basics", 1447), ("SQL in Practice", 591),
           ("Cooking Light", 1858), ("Salt and Stone", 321), ("Night Train", 479), ("Paper Moons", 2381)]
    got = rows(connect(SCHEMA_A), QUERY_C)
    assert same(got, exp), "days_old: use julianday(date) differences and CAST(... AS INTEGER) so you get 1758, not 1758.0."
    assert all(isinstance(r[1], int) for r in got), "days_old must be an INTEGER: wrap the subtraction in CAST(... AS INTEGER)."
    exp = [("Alpha", 1295), ("Beta", 731), ("Gamma", 730), ("Delta", 550), ("Epsilon", 1768), ("Sigma Book", 669), ("Omega", 1972)]
    assert same(rows(connect(SCHEMA_B), QUERY_C), exp), "QUERY_C on dataset B."
