import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def plan(db, sql, params=()):
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]



import random

from solution import INDEX, QUERY

NAIVE = "SELECT id, created FROM orders WHERE customer_id = ? ORDER BY created DESC, id DESC LIMIT 20"


def build(with_index):
    db = connect()
    db.execute("""CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, status TEXT NOT NULL,
                  created TEXT NOT NULL, total_paise INTEGER NOT NULL)""")
    rng = random.Random(15)
    rows = []
    for _ in range(12000):
        rows.append((rng.randint(1, 40), "open", f"2026-0{rng.randint(1, 3)}-{rng.randint(1, 9):02d}", rng.randint(1, 999)))
    rows += [(99, "open", "2026-05-05", 1)] * 5                 # a customer with 5 orders at the same moment
    db.executemany("INSERT INTO orders(customer_id, status, created, total_paise) VALUES (?,?,?,?)", rows)
    if with_index:
        db.execute(INDEX)
    return db


def test_one_placeholder_and_a_create_index():
    assert QUERY.count("?") == 1, "The query takes exactly one parameter: the customer id."
    assert INDEX.strip().upper().startswith("CREATE INDEX")


def test_the_plan_is_covering_and_has_no_sort():
    db = build(True)
    lines = plan(db, QUERY, (7,))
    text = " | ".join(lines)
    assert "COVERING INDEX" in text, f"The query must be answered from the index alone. Plan: {text}"
    assert "TEMP B-TREE" not in text, f"The sort must come from the index order, not from a temporary b-tree. Plan: {text}"
    assert "SEARCH" in text


def test_same_rows_as_the_naive_query():
    plain, indexed = build(False), build(True)
    for customer in list(range(1, 41)) + [99, 12345]:
        want = plain.execute(NAIVE, (customer,)).fetchall()
        got = indexed.execute(QUERY, (customer,)).fetchall()
        assert got == want, f"Customer {customer}: rows (and their order) must equal the naive query."
    assert len(indexed.execute(QUERY, (99,)).fetchall()) == 5
    assert len(indexed.execute(QUERY, (7,)).fetchall()) == 20
