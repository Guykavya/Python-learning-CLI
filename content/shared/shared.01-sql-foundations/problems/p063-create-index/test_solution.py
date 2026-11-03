import sqlite3
import pytest

from solution import SCRIPT

SCHEMA = """CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT, email TEXT);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);"""

Q1 = "SELECT * FROM orders WHERE customer_id = 7"
Q2 = "SELECT order_id FROM orders WHERE status = 'shipped' AND ordered >= '2024-03-01'"
Q3 = "SELECT order_id FROM orders WHERE customer_id = 7 ORDER BY ordered"


@pytest.fixture()
def con():
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA)
    for i in range(1, 301):
        c.execute("INSERT INTO customers VALUES (?, ?, ?)", (i, f"c{i}", f"c{i}@mail.test"))
    for i in range(1, 601):
        c.execute("INSERT INTO orders VALUES (?, ?, ?, ?)",
                  (i, i % 50, f"2024-0{1 + i % 6}-{1 + i % 28:02d}", "shipped" if i % 3 else "new"))
    try:
        c.executescript(SCRIPT)
    except sqlite3.Error as e:
        pytest.fail(f"SQLite rejected your script: {e}")
    return c


def plan(con, sql):
    return [r[3] for r in con.execute("EXPLAIN QUERY PLAN " + sql)]


def test_only_create_index_and_few(con):
    n = con.execute("SELECT COUNT(*) FROM sqlite_master WHERE type = 'index' AND sql IS NOT NULL").fetchone()[0]
    assert 1 <= n <= 3, f"You created {n} indexes; use between 1 and 3."


def test_customer_lookup_uses_index(con):
    p = plan(con, Q1)
    assert any("USING" in d and "INDEX" in d for d in p), f"Query 1 still scans the table: {p}. Index the column in the WHERE clause."


def test_status_date_uses_index(con):
    p = plan(con, Q2)
    assert any("SEARCH" in d and "INDEX" in d for d in p), f"Query 2 does not SEARCH with an index: {p}. Equality column first, then the range column."


def test_order_by_needs_no_sort(con):
    p = plan(con, Q3)
    assert any("INDEX" in d for d in p), f"Query 3 uses no index: {p}"
    assert not any("TEMP B-TREE" in d for d in p), f"Query 3 still sorts with a temporary B-tree: {p}. Make the index (customer_id, ordered) so rows come out sorted."


def test_email_is_unique(con):
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO customers VALUES (999, 'dup', 'c5@mail.test')")
