import sqlite3

import pytest

from solution import connect

SCHEMA = """
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id));
"""


def test_pragma_is_on():
    db = connect(":memory:")
    assert db.execute("PRAGMA foreign_keys").fetchone() == (1,), "Run PRAGMA foreign_keys = ON on every new connection."


def test_orphan_rows_are_refused():
    db = connect()
    db.executescript(SCHEMA)
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        db.execute("INSERT INTO orders VALUES (1, 99)")
    assert db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0


def test_valid_rows_still_work():
    db = connect()
    db.executescript(SCHEMA)
    db.execute("INSERT INTO customers VALUES (1, 'Asha')")
    db.execute("INSERT INTO orders VALUES (1, 1)")
    assert db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 1


def test_every_connection_to_a_file_has_it_on(tmp_path):
    path = str(tmp_path / "shop.db")
    a = connect(path)
    a.executescript(SCHEMA)
    a.commit()
    b = connect(path)
    assert b.execute("PRAGMA foreign_keys").fetchone() == (1,), "The setting is per connection: the second one needs it too."
    with pytest.raises(sqlite3.IntegrityError):
        b.execute("INSERT INTO orders VALUES (1, 5)")
    a.close()
    b.close()


def test_waits_for_a_locked_database(tmp_path):
    path = str(tmp_path / "lock.db")
    a = connect(path)
    a.execute("CREATE TABLE t (x)")
    a.commit()
    a.execute("BEGIN IMMEDIATE")           # a holds the write lock
    b = connect(path)
    import time
    t0 = time.monotonic()
    with pytest.raises(sqlite3.OperationalError):
        b.execute("INSERT INTO t VALUES (1)")
    waited = time.monotonic() - t0
    assert waited >= 4, f"Waited only {waited:.1f}s: connect with timeout=5 so short locks do not fail at once."
    a.rollback()
