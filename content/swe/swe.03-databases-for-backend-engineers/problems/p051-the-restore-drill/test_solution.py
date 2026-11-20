import os
import sqlite3

import pytest

from solution import RestoreFailed, fingerprint, restore_and_verify


def build(path):
    db = sqlite3.connect(path)
    db.executescript("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);
        CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, total_paise INTEGER, note TEXT, weight REAL);
        CREATE TABLE empty (id INTEGER PRIMARY KEY, label TEXT);
        INSERT INTO users VALUES (1, 'Asha', 30), (2, 'Ravi', NULL);
        INSERT INTO orders VALUES (1, 1, 500, 'a', 1.5), (2, 1, 1000, NULL, 2.25), (3, 2, 0, 'c', NULL);
    """)
    db.commit()
    return db


def make_backup(live, path):
    target = sqlite3.connect(path)
    live.backup(target)
    target.close()


def test_fingerprint_contents(tmp_path):
    live = build(str(tmp_path / "live.db"))
    fp = fingerprint(live)
    assert set(fp) == {"users", "orders", "empty"}, "Every user table, and no sqlite_* tables."
    assert fp["users"] == {"rows": 2, "sums": {"id": 3, "age": 30}}, f"Got {fp['users']}: sum the INTEGER/REAL columns, NULL counts as 0."
    assert fp["orders"] == {"rows": 3, "sums": {"id": 6, "user_id": 4, "total_paise": 1500, "weight": 3.75}}
    assert fp["empty"] == {"rows": 0, "sums": {"id": 0}}, "An empty table has 0 rows and sums of 0, not None."


def test_fingerprint_changes_when_data_changes(tmp_path):
    live = build(str(tmp_path / "live.db"))
    before = fingerprint(live)
    live.execute("UPDATE orders SET total_paise = total_paise + 1 WHERE id = 1")
    assert fingerprint(live) != before, "A changed amount must change the fingerprint."


def test_a_good_restore_returns_the_fingerprint(tmp_path):
    live = build(str(tmp_path / "live.db"))
    expected = fingerprint(live)
    make_backup(live, str(tmp_path / "b.bak"))
    got = restore_and_verify(str(tmp_path / "b.bak"), expected, str(tmp_path / "restored.db"))
    assert got == expected
    r = sqlite3.connect(str(tmp_path / "restored.db"))
    assert r.execute("SELECT COUNT(*) FROM orders").fetchone() == (3,), "The data must really be restored in dest_path."


def test_differing_tables_are_named(tmp_path):
    live = build(str(tmp_path / "live.db"))
    expected = fingerprint(live)
    make_backup(live, str(tmp_path / "b.bak"))
    live.execute("INSERT INTO orders VALUES (4, 2, 700, 'new', 1.0)")         # the live data moved on: expectation is stale
    live.execute("DELETE FROM users WHERE id = 2")
    stale = fingerprint(live)
    with pytest.raises(RestoreFailed) as e:
        restore_and_verify(str(tmp_path / "b.bak"), stale, str(tmp_path / "r.db"))
    msg = str(e.value)
    assert "orders" in msg and "users" in msg and "empty" not in msg, f"Name exactly the tables that differ. Got: {msg!r}"


def test_missing_and_extra_tables_count_as_differences(tmp_path):
    live = build(str(tmp_path / "live.db"))
    expected = fingerprint(live)
    make_backup(live, str(tmp_path / "b.bak"))
    extra = dict(expected, invoices={"rows": 0, "sums": {}})
    with pytest.raises(RestoreFailed, match="invoices"):
        restore_and_verify(str(tmp_path / "b.bak"), extra, str(tmp_path / "r1.db"))
    fewer = {k: v for k, v in expected.items() if k != "users"}
    with pytest.raises(RestoreFailed, match="users"):
        restore_and_verify(str(tmp_path / "b.bak"), fewer, str(tmp_path / "r2.db"))


def test_a_truncated_or_garbage_backup_fails_loudly(tmp_path):
    live = build(str(tmp_path / "live.db"))
    expected = fingerprint(live)
    make_backup(live, str(tmp_path / "b.bak"))
    data = open(str(tmp_path / "b.bak"), "rb").read()
    open(str(tmp_path / "half.bak"), "wb").write(data[: len(data) // 2])
    open(str(tmp_path / "head.bak"), "wb").write(data[:100])
    open(str(tmp_path / "junk.bak"), "wb").write(b"this is not a database at all" * 50)
    for name in ("half.bak", "head.bak", "junk.bak"):
        with pytest.raises(RestoreFailed):
            restore_and_verify(str(tmp_path / name), expected, str(tmp_path / f"r-{name}.db"))


def test_an_empty_backup_file_is_not_a_good_backup(tmp_path):
    live = build(str(tmp_path / "live.db"))
    expected = fingerprint(live)
    open(str(tmp_path / "empty.bak"), "wb").close()
    with pytest.raises(RestoreFailed):
        restore_and_verify(str(tmp_path / "empty.bak"), expected, str(tmp_path / "r.db"))


def test_restore_goes_into_a_fresh_file_only(tmp_path):
    live = build(str(tmp_path / "live.db"))
    expected = fingerprint(live)
    make_backup(live, str(tmp_path / "b.bak"))
    dest = str(tmp_path / "taken.db")
    open(dest, "wb").write(b"mine")
    with pytest.raises(FileExistsError):
        restore_and_verify(str(tmp_path / "b.bak"), expected, dest)
    assert open(dest, "rb").read() == b"mine"
