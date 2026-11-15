import sqlite3

from solution import upsert_if_newer


def row(id_, status, updated_at, amount="10.00"):
    return {"id": id_, "status": status, "amount": amount, "updated_at": updated_at}


def table(conn):
    return conn.execute("SELECT id, status, amount, updated_at FROM orders ORDER BY id").fetchall()


def test_inserts_into_an_empty_table():
    conn = sqlite3.connect(":memory:")
    n = upsert_if_newer(conn, [row(101, "pending", "2024-06-01T10:00:00Z", "19.99"),
                               row(102, "shipped", "2024-06-01T11:00:00Z", "5.00")])
    assert table(conn) == [(101, "pending", "19.99", "2024-06-01T10:00:00Z"),
                           (102, "shipped", "5.00", "2024-06-01T11:00:00Z")], (
        "Both new ids must be inserted with all four columns. Did you create the 'orders' table "
        "with the given schema?"
    )
    assert n == 2, f"Returned {n}; two rows were inserted, so return 2 (use cursor.rowcount)."


def test_example_newer_wins_stale_is_ignored():
    conn = sqlite3.connect(":memory:")
    upsert_if_newer(conn, [row(101, "pending", "2024-06-01T10:00:00Z"),
                           row(102, "pending", "2024-06-01T10:00:00Z")])
    n = upsert_if_newer(conn, [row(101, "shipped", "2024-06-01T12:00:00Z"),
                               row(102, "cancelled", "2024-06-01T09:00:00Z")])
    got = [(i, s) for i, s, _, _ in table(conn)]
    assert got == [(101, "shipped"), (102, "pending")], (
        f"Got {got}. 101 has a newer version (12:00 > 10:00) and must change; 102's incoming "
        "version is OLDER (09:00) and must be ignored. INSERT OR REPLACE / an unconditional "
        "DO UPDATE overwrites newer data with stale data. Add WHERE excluded.updated_at > orders.updated_at."
    )
    assert n == 1, f"Returned {n}; only 101 changed. The ignored stale row must not be counted."


def test_equal_timestamp_keeps_the_stored_row():
    conn = sqlite3.connect(":memory:")
    upsert_if_newer(conn, [row(7, "pending", "2024-06-01T10:00:00Z", "1.00")])
    n = upsert_if_newer(conn, [row(7, "shipped", "2024-06-01T10:00:00Z", "2.00")])
    assert table(conn) == [(7, "pending", "1.00", "2024-06-01T10:00:00Z")], (
        "Same updated_at means the same version: keep the stored row. Use '>' not '>='."
    )
    assert n == 0, f"Returned {n}; nothing changed, so return 0."


def test_running_the_same_batch_twice_changes_nothing():
    conn = sqlite3.connect(":memory:")
    batch = [row(i, "shipped", f"2024-06-0{i}T08:00:00Z") for i in range(1, 6)]
    assert upsert_if_newer(conn, batch) == 5
    before = table(conn)
    n = upsert_if_newer(conn, batch)
    assert table(conn) == before, "Loading the same batch again must leave the table identical."
    assert n == 0, (
        f"Second load of the same batch returned {n}. Nothing is newer, so nothing changes: 0."
    )
    assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 5, "No duplicate rows."


def test_repeated_id_inside_one_batch_any_order():
    conn = sqlite3.connect(":memory:")
    upsert_if_newer(conn, [row(1, "v2", "2024-06-02T00:00:00Z"),
                           row(1, "v3", "2024-06-03T00:00:00Z"),
                           row(1, "v1", "2024-06-01T00:00:00Z")])
    assert table(conn)[0][1] == "v3", (
        "The batch held v2, v3, v1 for the same id. The newest (v3) must survive even though "
        "v1 comes last. Insert-or-replace keeps whatever comes last."
    )
    assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 1, "One row per id."


def test_updates_all_columns_when_newer():
    conn = sqlite3.connect(":memory:")
    upsert_if_newer(conn, [row(5, "pending", "2024-06-01T10:00:00Z", "10.00")])
    upsert_if_newer(conn, [row(5, "shipped", "2024-06-01T10:00:01Z", "12.50")])
    assert table(conn) == [(5, "shipped", "12.50", "2024-06-01T10:00:01Z")], (
        "A newer version must overwrite status, amount AND updated_at. If updated_at is not "
        "updated, the next stale row compares against the old time."
    )


def test_stale_after_several_updates():
    conn = sqlite3.connect(":memory:")
    upsert_if_newer(conn, [row(9, "a", "2024-06-01T00:00:00Z")])
    upsert_if_newer(conn, [row(9, "b", "2024-06-05T00:00:00Z")])
    n = upsert_if_newer(conn, [row(9, "c", "2024-06-03T00:00:00Z")])
    assert table(conn)[0][1] == "b" and n == 0, (
        "06-03 is newer than the FIRST version but older than the stored one (06-05). Compare "
        "with the row currently in the table, and make sure updated_at was updated to 06-05."
    )


def test_mixed_counts():
    conn = sqlite3.connect(":memory:")
    upsert_if_newer(conn, [row(i, "old", "2024-06-01T10:00:00Z") for i in (1, 2, 3)])
    n = upsert_if_newer(conn, [
        row(1, "new", "2024-06-01T10:30:00Z"),   # update
        row(2, "old2", "2024-06-01T10:00:00Z"),  # equal: ignored
        row(3, "older", "2024-05-31T10:00:00Z"), # stale: ignored
        row(4, "new", "2024-06-01T10:00:00Z"),   # insert
        row(5, "new", "2024-06-01T10:00:00Z"),   # insert
    ])
    assert n == 3, f"Returned {n}; 1 update + 2 inserts = 3 rows written, 2 rows ignored."
    assert [s for _, s, _, _ in table(conn)] == ["new", "old", "old", "new", "new"]


def test_empty_batch():
    conn = sqlite3.connect(":memory:")
    assert upsert_if_newer(conn, []) == 0, "An empty batch writes nothing and returns 0."
    assert table(conn) == [], "The table must exist (CREATE TABLE IF NOT EXISTS) and be empty."


def test_changes_are_committed(tmp_path):
    path = tmp_path / "orders.db"
    conn = sqlite3.connect(path)
    upsert_if_newer(conn, [row(1, "shipped", "2024-06-01T10:00:00Z")])
    other = sqlite3.connect(path)          # a second connection sees only committed data
    got = other.execute("SELECT id, status FROM orders").fetchall()
    other.close()
    conn.close()
    assert got == [(1, "shipped")], (
        "Another connection cannot see the row: you did not commit. Call conn.commit() or "
        "use 'with conn:'."
    )


def test_parameters_not_string_formatting():
    conn = sqlite3.connect(":memory:")
    tricky = "it's shipped"
    upsert_if_newer(conn, [row(1, tricky, "2024-06-01T10:00:00Z")])
    assert table(conn)[0][1] == tricky, (
        "A status containing a quote broke your SQL. Pass values as parameters, never with f-strings."
    )
