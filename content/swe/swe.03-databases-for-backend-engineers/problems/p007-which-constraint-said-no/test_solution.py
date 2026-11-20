import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def plan(db, sql, params=()):
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]



import sqlite3

import pytest

from solution import attempt


@pytest.fixture
def db():
    d = connect()
    d.executescript("""
        CREATE TABLE parents (id INTEGER PRIMARY KEY);
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            age INTEGER CHECK (age >= 0),
            parent_id INTEGER REFERENCES parents(id)
        );
        INSERT INTO parents VALUES (1);
    """)
    return d


def test_ok(db):
    assert attempt(db, "INSERT INTO users(email, age, parent_id) VALUES ('a@x.com', 30, 1)") == "ok"
    assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1


@pytest.mark.parametrize("sql,kind", [
    ("INSERT INTO users(email) VALUES ('a@x.com')", "UNIQUE"),
    ("INSERT INTO users(id, email) VALUES (1, 'other@x.com')", "UNIQUE"),
    ("INSERT INTO users(email) VALUES (NULL)", "NOT NULL"),
    ("INSERT INTO users(email, age) VALUES ('b@x.com', -1)", "CHECK"),
    ("INSERT INTO users(email, parent_id) VALUES ('c@x.com', 99)", "FOREIGN KEY"),
])
def test_each_kind(db, sql, kind):
    db.execute("INSERT INTO users(id, email) VALUES (1, 'a@x.com')")
    assert attempt(db, sql) == kind, f"{sql!r} must report {kind}."
    assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1, "A refused statement leaves nothing behind."


def test_other_errors_propagate(db):
    with pytest.raises(sqlite3.OperationalError):
        attempt(db, "INSERT INTO nowhere VALUES (1)")
    with pytest.raises(sqlite3.OperationalError):
        attempt(db, "INSERT INTO users(email VALUES ('x')")


def test_the_connection_stays_usable(db):
    assert attempt(db, "INSERT INTO users(email) VALUES (NULL)") == "NOT NULL"
    assert attempt(db, "INSERT INTO users(email) VALUES ('ok@x.com')") == "ok"
