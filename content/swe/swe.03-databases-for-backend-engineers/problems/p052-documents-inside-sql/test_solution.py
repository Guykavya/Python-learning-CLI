import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def plan(db, sql, params=()):
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]



import json
import sqlite3

import pytest

from solution import find_by_attr


def test_sqlite_has_json_support():
    assert sqlite3.sqlite_version_info >= (3, 38), (
        f"SQLite {sqlite3.sqlite_version} is too old for the JSON functions this problem needs (3.38+). Update Python or SQLite.")


@pytest.fixture
def db():
    d = connect()
    d.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, attrs TEXT NOT NULL)")
    items = [
        ("Shirt", {"color": "red", "size": "M", "in_stock": True, "weight": 0.5}),
        ("Phone", {"color": "black", "storage_gb": 128, "in_stock": False}),
        ("Mug", {"color": "red", "note": "it's \"hot\""}),
        ("Cable", {}),
        ("TV", {"5\" screen": "yes", "a.b": "dot", "screen size": "large", "color": None}),
        ("Pen", {"color": "red", "in_stock": True}),
    ]
    d.executemany("INSERT INTO products(name, attrs) VALUES (?, ?)", [(n, json.dumps(a)) for n, a in items])
    d.commit()
    return d


def test_string_values(db):
    assert find_by_attr(db, "color", "red") == [1, 3, 6]
    assert find_by_attr(db, "color", "black") == [2]
    assert find_by_attr(db, "color", "green") == []


def test_numbers_and_booleans(db):
    assert find_by_attr(db, "storage_gb", 128) == [2]
    assert find_by_attr(db, "weight", 0.5) == [1]
    assert find_by_attr(db, "in_stock", True) == [1, 6], "JSON true is matched by Python True."
    assert find_by_attr(db, "in_stock", False) == [2]


def test_a_missing_key_never_matches(db):
    assert find_by_attr(db, "size", "M") == [1]
    assert find_by_attr(db, "nothing", "x") == []
    assert 4 not in find_by_attr(db, "color", "red"), "The product with {} has no color key."


def test_values_with_quotes(db):
    assert find_by_attr(db, "note", 'it\'s "hot"') == [3], "The value is a bound parameter: quotes are harmless."
    assert find_by_attr(db, "color", "' OR 1=1 --") == []


def test_keys_with_dots_spaces_and_quotes(db):
    assert find_by_attr(db, "a.b", "dot") == [5], "A dot in a key is part of the key, not a path separator."
    assert find_by_attr(db, "screen size", "large") == [5]
    assert find_by_attr(db, '5" screen', "yes") == [5]
    assert find_by_attr(db, "color.x", "red") == [], "'color.x' is not 'color'."


@pytest.mark.parametrize("bad", [None, [1], {"a": 1}, b"x"])
def test_bad_values(db, bad):
    with pytest.raises(ValueError):
        find_by_attr(db, "color", bad)


def test_the_result_is_sorted_ids(db):
    ids = find_by_attr(db, "color", "red")
    assert ids == sorted(ids) and all(isinstance(i, int) for i in ids)
