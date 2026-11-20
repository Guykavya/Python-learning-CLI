import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def plan(db, sql, params=()):
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]



import random

from solution import INDEXES


def build():
    db = connect()
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL, name TEXT NOT NULL)")
    db.execute("CREATE TABLE tickets (id INTEGER PRIMARY KEY, created TEXT NOT NULL, status TEXT NOT NULL, subject TEXT NOT NULL)")
    rng = random.Random(16)
    db.executemany("INSERT INTO users(email, name) VALUES (?, ?)", [(f"User{i}@Example.com", f"u{i}") for i in range(5000)])
    db.executemany("INSERT INTO tickets(created, status, subject) VALUES (?,?,?)",
                   [(f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}", "open" if i % 100 == 0 else "closed", f"s{i}")
                    for i in range(10000)])
    for s in INDEXES:
        db.execute(s)
    return db


def test_exactly_two_create_index_statements():
    assert len(INDEXES) == 2 and all(s.strip().upper().startswith("CREATE INDEX") for s in INDEXES)


def test_login_query_uses_the_expression_index():
    db = build()
    lines = plan(db, "SELECT id FROM users WHERE lower(email) = ?", ("user42@example.com",))
    assert any("SEARCH" in l and "USING" in l for l in lines), (
        f"Q1 still scans: {lines}. Index the EXPRESSION lower(email); a plain index on email cannot be used.")
    assert db.execute("SELECT name FROM users WHERE lower(email) = ?", ("user42@example.com",)).fetchall() == [("u42",)]
    lines = plan(db, "SELECT id FROM users WHERE LOWER(email) = ?", ("x",))
    assert any("SEARCH" in l for l in lines), "LOWER(email) is the same expression as lower(email)."


def test_open_tickets_use_a_partial_index_without_a_sort():
    db = build()
    text = " | ".join(plan(db, "SELECT id FROM tickets WHERE status = 'open' ORDER BY created"))
    assert "USING" in text and "INDEX" in text, f"Q2 must use an index: {text}"
    assert "TEMP B-TREE" not in text, f"Index the column 'created' so the ORDER BY is free. Plan: {text}"


def test_the_index_is_really_partial():
    db = build()
    sqls = [r[0] for r in db.execute("SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='tickets' AND sql IS NOT NULL")]
    assert any("WHERE" in s.upper() and "'open'" in s for s in sqls), "The ticket index must end with WHERE status = 'open'."


def test_closed_tickets_do_not_use_the_partial_index():
    db = build()
    lines = plan(db, "SELECT id FROM tickets WHERE status = 'closed' ORDER BY created")
    assert not any("idx_tickets" in l.lower() or "USING INDEX" in l for l in lines), (
        f"A partial index on open tickets cannot answer a query for closed ones: {lines}")


def test_results_are_correct():
    db = build()
    got = db.execute("SELECT id FROM tickets WHERE status = 'open' ORDER BY created").fetchall()
    assert len(got) == 100
