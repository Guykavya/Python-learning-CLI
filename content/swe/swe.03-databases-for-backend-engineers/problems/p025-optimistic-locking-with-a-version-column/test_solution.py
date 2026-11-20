import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def plan(db, sql, params=()):
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]



import pytest

from solution import update_price


@pytest.fixture
def db():
    d = connect()
    d.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, price_paise INTEGER NOT NULL, version INTEGER NOT NULL DEFAULT 1)")
    d.execute("INSERT INTO products VALUES (1, 10000, 1), (2, 500, 5)")
    d.commit()
    return d


def row(db, pid=1):
    return db.execute("SELECT price_paise, version FROM products WHERE id = ?", (pid,)).fetchone()


def test_first_writer_wins_second_loses(db):
    assert update_price(db, 1, 12000, 1) is True
    assert row(db) == (12000, 2), "The price changes and the version goes from 1 to 2."
    assert update_price(db, 1, 9000, 1) is False
    assert row(db) == (12000, 2), "The second editor saw version 1: nothing may change."


def test_retry_with_the_new_version_works(db):
    update_price(db, 1, 12000, 1)
    assert update_price(db, 1, 9000, 2) is True
    assert row(db) == (9000, 3)


def test_other_rows_are_not_touched(db):
    update_price(db, 1, 1, 1)
    assert row(db, 2) == (500, 5)


def test_wrong_or_future_version_and_missing_row(db):
    assert update_price(db, 2, 1, 4) is False
    assert update_price(db, 2, 1, 6) is False
    assert update_price(db, 99, 1, 1) is False
    assert row(db, 2) == (500, 5)


def test_the_change_is_committed(db, tmp_path):
    path = str(tmp_path / "p.db")
    a = connect(path)
    a.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, price_paise INTEGER NOT NULL, version INTEGER NOT NULL DEFAULT 1)")
    a.execute("INSERT INTO products VALUES (1, 100, 1)")
    a.commit()
    assert update_price(a, 1, 200, 1) is True
    assert connect(path).execute("SELECT price_paise, version FROM products").fetchone() == (200, 2), "Commit a successful update."
    assert not a.in_transaction


def test_two_connections_race(tmp_path):
    path = str(tmp_path / "p.db")
    a, b = connect(path), connect(path)
    a.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, price_paise INTEGER NOT NULL, version INTEGER NOT NULL DEFAULT 1)")
    a.execute("INSERT INTO products VALUES (1, 100, 1)")
    a.commit()
    assert (update_price(a, 1, 150, 1), update_price(b, 1, 175, 1)) == (True, False)
    assert a.execute("SELECT price_paise FROM products").fetchone() == (150,)
