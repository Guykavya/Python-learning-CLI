import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def plan(db, sql, params=()):
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]



import sqlite3

import pytest

from solution import SCHEMA


@pytest.fixture
def db():
    d = connect()
    d.executescript(SCHEMA)
    return d


def test_basic_insert_and_live_duplicate(db):
    db.execute("INSERT INTO customers(email, name) VALUES ('a@x.com', 'Asha')")
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
        db.execute("INSERT INTO customers(email, name) VALUES ('a@x.com', 'Copy')")


def test_a_deleted_email_can_be_registered_again(db):
    db.execute("INSERT INTO customers(email, name) VALUES ('a@x.com', 'Asha')")
    db.execute("UPDATE customers SET deleted_at = '2026-01-01' WHERE id = 1")
    db.execute("INSERT INTO customers(email, name) VALUES ('a@x.com', 'Asha again')")
    assert db.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 2, "The old row stays (soft delete)."
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO customers(email, name) VALUES ('a@x.com', 'Third')")


def test_many_deleted_rows_may_share_an_email(db):
    for i in range(3):
        db.execute("INSERT INTO customers(email, name) VALUES ('a@x.com', ?)", (f"n{i}",))
        db.execute("UPDATE customers SET deleted_at = '2026-01-0' || ? WHERE deleted_at IS NULL", (i + 1,))
    assert db.execute("SELECT COUNT(*) FROM customers WHERE email='a@x.com'").fetchone()[0] == 3


def test_undeleting_into_a_conflict_fails(db):
    db.execute("INSERT INTO customers(email, name) VALUES ('a@x.com', 'Old')")
    db.execute("UPDATE customers SET deleted_at = 'x' WHERE id = 1")
    db.execute("INSERT INTO customers(email, name) VALUES ('a@x.com', 'New')")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("UPDATE customers SET deleted_at = NULL WHERE id = 1")


def test_the_view_shows_only_live_customers(db):
    db.execute("INSERT INTO customers(email, name) VALUES ('a@x.com', 'Asha')")
    db.execute("INSERT INTO customers(email, name) VALUES ('b@x.com', 'Ravi')")
    db.execute("UPDATE customers SET deleted_at = 'x' WHERE email = 'a@x.com'")
    rows = db.execute("SELECT id, email, name FROM active_customers").fetchall()
    assert rows == [(2, "b@x.com", "Ravi")], f"active_customers must list live customers only, with the columns id, email, name; got {rows}."
    assert [r[1] for r in db.execute("PRAGMA table_info(active_customers)")] == ["id", "email", "name"]


def test_email_column_has_no_plain_unique_constraint(db):
    sql = db.execute("SELECT sql FROM sqlite_master WHERE name = 'customers'").fetchone()[0].upper()
    assert "UNIQUE" not in sql, "A plain UNIQUE on the column blocks re-registration: use a partial unique index."
    idx = [r[0] for r in db.execute("SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")]
    assert any("UNIQUE" in s.upper() and "WHERE" in s.upper() for s in idx), "Create a UNIQUE INDEX ... WHERE deleted_at IS NULL."
