import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def plan(db, sql, params=()):
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]



import sqlite3

import pytest

from solution import place_order


@pytest.fixture
def db(tmp_path):
    d = connect(str(tmp_path / "shop.db"))
    d.executescript("""
        CREATE TABLE products (sku TEXT PRIMARY KEY, stock INTEGER NOT NULL CHECK (stock >= 0));
        CREATE TABLE orders (id INTEGER PRIMARY KEY, sku TEXT NOT NULL REFERENCES products(sku), qty INTEGER NOT NULL CHECK (qty > 0));
        INSERT INTO products VALUES ('TEA', 10), ('BAD', 10);
        CREATE TRIGGER no_bad_update BEFORE UPDATE ON products WHEN OLD.sku = 'BAD'
        BEGIN SELECT RAISE(ABORT, 'boom'); END;
    """)
    d.commit()
    return d


def stock(db, sku="TEA"):
    return db.execute("SELECT stock FROM products WHERE sku = ?", (sku,)).fetchone()[0]


def n_orders(db):
    return db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]


def test_success_returns_the_order_id_and_updates_stock(db):
    assert place_order(db, "TEA", 3) == 1
    assert place_order(db, "TEA", 2) == 2
    assert stock(db) == 5 and n_orders(db) == 2
    assert not db.in_transaction, "Commit before returning."


def test_selling_exactly_the_stock(db):
    place_order(db, "TEA", 10)
    assert stock(db) == 0


def test_insufficient_stock_leaves_no_trace(db):
    place_order(db, "TEA", 8)
    with pytest.raises(ValueError, match="insufficient"):
        place_order(db, "TEA", 3)
    assert stock(db) == 2 and n_orders(db) == 1, "No order row and no stock change after a refusal."
    assert not db.in_transaction, "The failed attempt must roll back: do not leave the transaction open."


def test_unknown_product_and_bad_quantity(db):
    with pytest.raises(LookupError):
        place_order(db, "NOPE", 1)
    with pytest.raises(ValueError):
        place_order(db, "TEA", 0)
    with pytest.raises(ValueError):
        place_order(db, "TEA", -2)
    assert n_orders(db) == 0 and not db.in_transaction


def test_a_failure_after_the_insert_undoes_the_insert(db):
    with pytest.raises(sqlite3.DatabaseError):
        place_order(db, "BAD", 1)            # the trigger aborts the stock UPDATE
    assert n_orders(db) == 0, "The order row was inserted before the failing UPDATE: it must be rolled back."
    assert stock(db, "BAD") == 10 and not db.in_transaction


def test_the_write_lock_is_taken_first(db, tmp_path):
    other = connect(str(tmp_path / "shop.db"))
    other.execute("BEGIN IMMEDIATE")           # somebody else is writing
    short = connect(str(tmp_path / "shop.db"))
    short.execute("PRAGMA busy_timeout = 100")
    with pytest.raises(sqlite3.OperationalError, match="locked"):
        place_order(short, "TEA", 1)
    assert not short.in_transaction, "If the lock cannot be taken, nothing must stay open."
    other.rollback()
