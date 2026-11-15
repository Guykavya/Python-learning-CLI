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
CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER,
  ordered     TEXT NOT NULL,
  status      TEXT NOT NULL      -- 'shipped', 'pending' or 'cancelled'
);
CREATE TABLE order_items (
  order_id   INTEGER NOT NULL,
  book_id    INTEGER NOT NULL,
  qty        INTEGER NOT NULL,
  unit_price REAL NOT NULL,       -- price when sold; may differ from books.price
  PRIMARY KEY (order_id, book_id)
);
INSERT INTO orders VALUES
 (1, 1, '2024-01-05', 'shipped'),
 (2, 1, '2024-02-10', 'shipped'),
 (3, 2, '2024-02-11', 'cancelled'),
 (4, 3, '2024-03-01', 'shipped'),
 (5, 5, '2024-03-15', 'pending');
INSERT INTO order_items VALUES
 (1, 1, 2, 12.50), (1, 3, 1, 39.00), (2, 5, 1, 18.00), (3, 2, 1, 9.99),
 (4, 7, 3, 9.99),  (4, 8, 1, 14.25), (5, 4, 1, 45.50);
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
CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER,
  ordered     TEXT NOT NULL,
  status      TEXT NOT NULL      -- 'shipped', 'pending' or 'cancelled'
);
CREATE TABLE order_items (
  order_id   INTEGER NOT NULL,
  book_id    INTEGER NOT NULL,
  qty        INTEGER NOT NULL,
  unit_price REAL NOT NULL,       -- price when sold; may differ from books.price
  PRIMARY KEY (order_id, book_id)
);
INSERT INTO orders VALUES
 (1, 1, '2024-01-01', 'shipped'),
 (2, 2, '2024-01-02', 'cancelled'),
 (3, 2, '2024-01-03', 'shipped');
INSERT INTO order_items VALUES
 (1, 1, 3, 9.00), (1, 3, 2, 20.00), (2, 2, 1, 20.00), (3, 4, 4, 4.50), (3, 5, 1, 5.50);
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
    assert colnames(connect(SCHEMA_A), QUERY) == ["order_id", "title", "line_total"], "Columns: order_id, title, line_total."


def test_dataset_a():
    exp = [(1, "Data Basics", 39.0), (1, "Quiet Rivers", 25.0), (2, "Cooking Light", 18.0),
           (4, "Night Train", 29.97), (4, "Paper Moons", 14.25)]
    assert rows(connect(SCHEMA_A), QUERY) == exp, \
        "Expected 5 lines of shipped orders 1, 2, 4, sorted by order_id then title, with ROUND(qty * unit_price, 2)."


def test_dataset_b_uses_sale_price():
    exp = [(1, "Alpha", 27.0), (1, "Gamma", 40.0), (3, "Delta", 18.0), (3, "Epsilon", 5.5)]
    assert rows(connect(SCHEMA_B), QUERY) == exp, \
        "Use order_items.unit_price (the price when sold), not books.price. Cancelled order 2 must not appear."
