import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def plan(db, sql, params=()):
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]



import pytest

from solution import SCHEMA


def fresh():
    db = connect()
    db.executescript(SCHEMA)
    return db


def columns(db, table):
    return {r[1]: {"type": r[2].upper(), "notnull": bool(r[3]), "pk": r[5]} for r in db.execute(f"PRAGMA table_info({table})")}


def test_tables_and_columns_exist():
    db = fresh()
    names = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"customers", "books", "orders", "order_lines"} <= names
    assert set(columns(db, "customers")) == {"id", "email", "name"}
    assert set(columns(db, "books")) == {"id", "title", "price_paise"}
    assert set(columns(db, "orders")) == {"id", "customer_id", "placed_at"}
    assert set(columns(db, "order_lines")) == {"order_id", "book_id", "qty", "price_paise"}


def test_money_and_quantities_are_integers_and_not_null():
    db = fresh()
    assert columns(db, "books")["price_paise"]["type"] == "INTEGER", "Money in paise: INTEGER, not REAL."
    for col in ("qty", "price_paise"):
        c = columns(db, "order_lines")[col]
        assert c["type"] == "INTEGER" and c["notnull"], f"order_lines.{col} must be INTEGER NOT NULL."
    for table, col in (("customers", "email"), ("customers", "name"), ("books", "title"), ("books", "price_paise"),
                       ("orders", "customer_id"), ("orders", "placed_at"), ("order_lines", "order_id"), ("order_lines", "book_id")):
        assert columns(db, table)[col]["notnull"], f"{table}.{col} must be NOT NULL."


def test_composite_primary_key_of_the_lines():
    db = fresh()
    pk = {c: v["pk"] for c, v in columns(db, "order_lines").items() if v["pk"]}
    assert set(pk) == {"order_id", "book_id"}, "order_lines needs PRIMARY KEY (order_id, book_id)."


def test_foreign_keys_are_declared():
    db = fresh()
    fks = {(t, r[3], r[2], r[4]) for t in ("orders", "order_lines") for r in db.execute(f"PRAGMA foreign_key_list({t})")}
    assert ("orders", "customer_id", "customers", "id") in fks
    assert ("order_lines", "order_id", "orders", "id") in fks
    assert ("order_lines", "book_id", "books", "id") in fks


GOOD = [
    "INSERT INTO customers VALUES (1, 'a@x.com', 'Asha')",
    "INSERT INTO books VALUES (1, 'Dune', 50000)",
    "INSERT INTO orders VALUES (1, 1, '2026-01-01')",
    "INSERT INTO order_lines VALUES (1, 1, 2, 50000)",
]


@pytest.mark.parametrize("bad,reason", [
    ("INSERT INTO customers VALUES (2, 'a@x.com', 'Other')", "UNIQUE"),
    ("INSERT INTO customers VALUES (2, NULL, 'Other')", "NOT NULL"),
    ("INSERT INTO books VALUES (2, 'Free?', -5)", "CHECK"),
    ("INSERT INTO order_lines VALUES (1, 1, 3, 100)", "UNIQUE"),
    ("INSERT INTO books VALUES (3, 'Dune 2', 1000); INSERT INTO order_lines VALUES (1, 3, 0, 100)", "CHECK"),
    ("INSERT INTO orders VALUES (2, 99, '2026-01-02')", "FOREIGN KEY"),
])
def test_bad_inserts_are_refused_for_the_right_reason(bad, reason):
    db = fresh()
    for sql in GOOD:
        db.execute(sql)
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError) as e:
        db.executescript(bad)
    assert reason in str(e.value), f"Expected a {reason} violation, got: {e.value}"
