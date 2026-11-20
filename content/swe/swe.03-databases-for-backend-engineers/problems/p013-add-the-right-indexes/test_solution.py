import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def plan(db, sql, params=()):
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]



import random

from solution import INDEXES

QUERIES = {
    "A": ("SELECT * FROM orders WHERE customer_id = ?", (7,)),
    "B": ("SELECT * FROM orders WHERE status = ? AND created >= ?", ("open", "2026-06-01")),
    "C": ("SELECT * FROM orders WHERE customer_id = ? AND status = ?", (7, "open")),
}


def build():
    db = connect()
    db.execute("""CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, status TEXT NOT NULL,
                  created TEXT NOT NULL, total_paise INTEGER NOT NULL)""")
    rng = random.Random(13)
    rows = [(rng.randint(1, 500), rng.choice(["open", "paid", "shipped", "cancelled"]),
             f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}", rng.randint(100, 100000)) for _ in range(20000)]
    db.executemany("INSERT INTO orders(customer_id, status, created, total_paise) VALUES (?,?,?,?)", rows)
    return db


def test_at_most_three_index_statements():
    assert isinstance(INDEXES, list) and 1 <= len(INDEXES) <= 3, (
        f"Use between 1 and 3 indexes (you have {len(INDEXES)}): one index per column is not a strategy.")
    for s in INDEXES:
        assert s.strip().upper().startswith("CREATE INDEX"), f"Every statement must start with CREATE INDEX: {s!r}"


def test_every_query_is_searched():
    db = build()
    for sql in INDEXES:
        db.execute(sql)
    for name, (sql, params) in QUERIES.items():
        lines = plan(db, sql, params)
        assert any("SEARCH" in line for line in lines), f"Query {name} still scans the table: {lines}. Add an index it can use."
        assert not any(line.startswith("SCAN") for line in lines), f"Query {name} plan has a SCAN: {lines}"


def test_queries_give_the_same_rows_with_and_without_indexes():
    plain, indexed = build(), build()
    for sql in INDEXES:
        indexed.execute(sql)
    for name, (sql, params) in QUERIES.items():
        a = sorted(plain.execute(sql, params).fetchall())
        b = sorted(indexed.execute(sql, params).fetchall())
        assert a == b and a, f"Query {name}: indexes must not change the result."


def test_the_table_is_untouched():
    db = build()
    for sql in INDEXES:
        db.execute(sql)
    assert db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 20000
