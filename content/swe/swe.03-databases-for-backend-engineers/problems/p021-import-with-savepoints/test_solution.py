import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def plan(db, sql, params=()):
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]



import sqlite3

import pytest

from solution import import_rows

SCHEMA = "CREATE TABLE products (sku TEXT NOT NULL UNIQUE, qty INTEGER NOT NULL CHECK (qty > 0))"


@pytest.fixture
def paths(tmp_path):
    return str(tmp_path / "shop.db")


@pytest.fixture
def db(paths):
    d = connect(paths)
    d.execute(SCHEMA)
    d.commit()
    return d


def stored(path):
    other = connect(path)
    return other.execute("SELECT sku, qty FROM products ORDER BY sku").fetchall()


def test_good_rows_are_committed(db, paths):
    assert import_rows(db, [("a", 5), ("b", 7)]) == []
    assert stored(paths) == [("a", 5), ("b", 7)], "The rows must be committed and visible to another connection."
    assert not db.in_transaction


def test_bad_rows_are_reported_and_good_ones_kept(db, paths):
    errors = import_rows(db, [("a", 5), ("a", 2), ("b", 0), ("c", 7), ("d", None)])
    assert [line for line, _ in errors] == [2, 3, 5], f"Bad rows are lines 2 (UNIQUE), 3 (CHECK) and 5 (NOT NULL): {errors}"
    assert "UNIQUE" in errors[0][1] and "CHECK" in errors[1][1] and "NOT NULL" in errors[2][1]
    assert stored(paths) == [("a", 5), ("c", 7)], "Good rows before and after the bad ones stay."


def test_a_row_that_fails_leaves_no_trace(db, paths):
    import_rows(db, [("x", 1), ("x", 2)])
    assert stored(paths) == [("x", 1)]


def test_unexpected_error_rolls_back_the_good_rows(db, paths):
    class Boom:
        pass

    with pytest.raises(sqlite3.Error):
        import_rows(db, [("a", 1), ("b", Boom())])
    assert stored(paths) == [], "An error that is not an IntegrityError must undo the whole import."
    assert not db.in_transaction


def test_empty_import(db):
    assert import_rows(db, []) == []


def test_importing_into_a_table_with_existing_rows(db, paths):
    db.execute("INSERT INTO products VALUES ('old', 3)")
    db.commit()
    errors = import_rows(db, [("old", 1), ("new", 2)])
    assert [l for l, _ in errors] == [1]
    assert stored(paths) == [("new", 2), ("old", 3)]
