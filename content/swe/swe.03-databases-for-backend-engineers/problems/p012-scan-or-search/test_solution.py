import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def plan(db, sql, params=()):
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]



import pytest

from solution import uses_index


@pytest.fixture
def db():
    d = connect()
    d.executescript("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, city TEXT, age INTEGER);
        CREATE INDEX idx_email ON users(email);
        CREATE INDEX idx_city_age ON users(city, age);
    """)
    return d


@pytest.mark.parametrize("sql,params,expected", [
    ("SELECT * FROM users WHERE id = 5", (), True),
    ("SELECT * FROM users WHERE email = ?", ("a@x.com",), True),
    ("SELECT * FROM users WHERE city = ? AND age > ?", ("Pune", 30), True),
    ("SELECT * FROM users WHERE age = ?", (30,), False),
    ("SELECT * FROM users WHERE email LIKE '%x.com'", (), False),
    ("SELECT * FROM users WHERE lower(email) = ?", ("a@x.com",), False),
    ("SELECT * FROM users", (), False),
])
def test_plans(db, sql, params, expected):
    assert uses_index(db, sql, params) is expected, f"{sql!r}: expected {expected}. Look for the word SEARCH in the plan."


def test_does_not_run_the_query(db):
    db.execute("INSERT INTO users(email) VALUES ('a@x.com')")
    uses_index(db, "DELETE FROM users WHERE email = ?", ("a@x.com",))
    assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1, "Only the plan is asked for: the DELETE must not run."


def test_join_with_one_searched_table(db):
    db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER)")
    sql = "SELECT * FROM orders o JOIN users u ON u.id = o.user_id"
    assert uses_index(db, sql) is True, "The join searches users by primary key."
