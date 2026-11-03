import json
import sqlite3

import pytest

from solution import build_clean, load_raw

COLUMNS = ["id", "email", "city", "status", "amount_cents", "currency", "created_at", "item_count"]


def order(i, email="asha@example.com", city="Pune", status="shipped", amount="19.99", currency="INR",
          items=({"sku": "B1", "qty": 2},)):
    return {"id": i, "customer": {"email": email, "city": city}, "status": status, "amount": amount,
            "currency": currency, "created_at": "2024-06-01T10:00:00Z",
            "updated_at": "2024-06-01T12:00:00Z", "items": list(items)}


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    yield c
    c.close()


def clean_rows(conn):
    return conn.execute("SELECT * FROM clean_orders ORDER BY id").fetchall()


def test_load_raw_stores_text_exactly(conn):
    texts = ['{"id": 1,   "status": "shipped"}', '{\n  "id": 2\n}', '{"b": 1, "a": 2}']
    assert load_raw(conn, texts, "2024-06-02T01:00:00Z") == 3, "load_raw returns how many rows it inserted."
    stored = conn.execute("SELECT loaded_at, payload FROM raw_orders ORDER BY raw_id").fetchall()
    assert stored == [("2024-06-02T01:00:00Z", t) for t in texts], (
        f"Stored {stored}. The raw layer keeps the text exactly as received: do not json.loads and json.dumps it "
        "(that changes spacing and key order), and store loaded_at with every row."
    )


def test_load_raw_keeps_invalid_json(conn):
    load_raw(conn, ['{"id": 1}', '{"id": 2, broken', ''], "t1")
    count = conn.execute("SELECT COUNT(*) FROM raw_orders").fetchone()[0]
    assert count == 3, (
        f"raw_orders has {count} rows. Keep invalid payloads too: the raw layer is the evidence of what arrived. "
        "The clean step filters them."
    )


def test_load_raw_appends_and_uses_parameters(conn):
    load_raw(conn, [json.dumps(order(1, city="O'Brien Nagar"))], "t1")
    assert load_raw(conn, [json.dumps(order(2)), json.dumps(order(3))], "t2") == 2
    rows = conn.execute("SELECT loaded_at, COUNT(*) FROM raw_orders GROUP BY loaded_at ORDER BY loaded_at").fetchall()
    assert rows == [("t1", 1), ("t2", 2)], (
        f"Got {rows}. A second load appends (CREATE TABLE IF NOT EXISTS, not DROP), and a city with a quote "
        "must work: use ? parameters."
    )


def test_load_raw_commits(tmp_path):
    path = tmp_path / "warehouse.db"
    c = sqlite3.connect(path)
    load_raw(c, [json.dumps(order(1))], "t1")
    other = sqlite3.connect(path)
    count = other.execute("SELECT COUNT(*) FROM raw_orders").fetchone()[0]
    other.close()
    c.close()
    assert count == 1, "Another connection sees no rows. Call conn.commit() at the end of load_raw."


def test_clean_table_columns_and_values(conn):
    load_raw(conn, [json.dumps(order(101, email=" Asha@Example.com", status="Shipped ", currency="inr",
                                     items=[{"sku": "B1", "qty": 2}, {"sku": "C7", "qty": 1}]))], "t1")
    assert build_clean(conn) == 1, "build_clean returns the number of rows in clean_orders."
    names = [row[1] for row in conn.execute("PRAGMA table_info(clean_orders)")]
    assert names == COLUMNS, f"clean_orders columns were {names}; expected {COLUMNS} in that order."
    assert clean_rows(conn) == [(101, "asha@example.com", "Pune", "shipped", 1999, "INR", "2024-06-01T10:00:00Z", 2)], (
        f"Row was {clean_rows(conn)}. Check trim/lower on email and status, upper on currency, "
        "json_array_length for item_count."
    )


def test_amount_cents_are_rounded_integers(conn):
    amounts = {1: "19.99", 2: "0.29", 3: "5", 4: "1234.5", 5: "0.07", 6: "4.35"}
    load_raw(conn, [json.dumps(order(i, amount=a)) for i, a in amounts.items()], "t1")
    build_clean(conn)
    got = dict(conn.execute("SELECT id, amount_cents FROM clean_orders"))
    assert got == {1: 1999, 2: 29, 3: 500, 4: 123450, 5: 7, 6: 435}, (
        f"amount_cents were {got}. 19.99 * 100 is 1998.9999999999998 in floating point and CAST cuts it to 1998: "
        "ROUND(... * 100) first, then CAST AS INTEGER."
    )
    types = {t for (t,) in conn.execute("SELECT DISTINCT typeof(amount_cents) FROM clean_orders")}
    assert types == {"integer"}, f"typeof(amount_cents) was {types}; cast the rounded value to INTEGER."


def test_city_null_and_blank_become_sql_null(conn):
    load_raw(conn, [json.dumps(order(1, city=None)), json.dumps(order(2, city="   ")),
                    json.dumps(order(3, city="  Goa "))], "t1")
    build_clean(conn)
    got = conn.execute("SELECT id, city, typeof(city) FROM clean_orders ORDER BY id").fetchall()
    assert got == [(1, None, "null"), (2, None, "null"), (3, "Goa", "text")], (
        f"Got {got}. JSON null must be SQL NULL (not the text 'null'), a blank city must become NULL "
        "(NULLIF(trim(...), '')), and other cities are trimmed."
    )


def test_invalid_payloads_are_skipped_not_fatal(conn):
    load_raw(conn, [json.dumps(order(1)), '{"id": 2, broken', "", "[not json", json.dumps(order(3))], "t1")
    assert build_clean(conn) == 2, (
        "Only the two valid payloads become clean rows. Without WHERE json_valid(payload), "
        "json_extract raises 'malformed JSON' and the whole build fails."
    )
    assert [r[0] for r in clean_rows(conn)] == [1, 3]


def test_types_are_integers(conn):
    load_raw(conn, [json.dumps(order(7, items=[]))], "t1")
    build_clean(conn)
    got = conn.execute("SELECT typeof(id), typeof(item_count), item_count FROM clean_orders").fetchone()
    assert got == ("integer", "integer", 0), f"Got {got}. id and item_count must be integers; no items gives 0."


def test_rebuild_is_repeatable_and_follows_raw(conn):
    load_raw(conn, [json.dumps(order(1)), json.dumps(order(2))], "t1")
    assert build_clean(conn) == 2
    assert build_clean(conn) == 2, (
        "Building twice must give the same table. DROP TABLE IF EXISTS clean_orders before CREATE TABLE ... AS SELECT "
        "(and do not INSERT into an existing clean table)."
    )
    load_raw(conn, [json.dumps(order(3, status="pending"))], "t2")
    assert build_clean(conn) == 3, "After more raw rows arrive, a rebuild includes them."
    assert [r[3] for r in clean_rows(conn)] == ["shipped", "shipped", "pending"]


def test_build_reads_from_the_raw_table(conn):
    conn.execute("CREATE TABLE raw_orders (raw_id INTEGER PRIMARY KEY, loaded_at TEXT NOT NULL, payload TEXT NOT NULL)")
    conn.execute("INSERT INTO raw_orders (loaded_at, payload) VALUES (?, ?)",
                 ("old", json.dumps(order(55, email="MEERA@EXAMPLE.COM", amount="2.50", currency="usd"))))
    conn.commit()
    assert build_clean(conn) == 1, (
        "build_clean must transform whatever is in raw_orders (rows loaded months ago too), "
        "not data kept in Python from load_raw."
    )
    assert clean_rows(conn) == [(55, "meera@example.com", "Pune", "shipped", 250, "USD", "2024-06-01T10:00:00Z", 1)]


def test_build_commits(tmp_path):
    path = tmp_path / "warehouse.db"
    c = sqlite3.connect(path)
    load_raw(c, [json.dumps(order(1))], "t1")
    build_clean(c)
    other = sqlite3.connect(path)
    count = other.execute("SELECT COUNT(*) FROM clean_orders").fetchone()[0]
    other.close()
    c.close()
    assert count == 1, "Another connection cannot see clean_orders. Commit at the end of build_clean."
