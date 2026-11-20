import os
import sqlite3
import threading

import pytest

from solution import backup


def make(path, rows=100):
    db = sqlite3.connect(path)
    db.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, pad TEXT)")
    db.executemany("INSERT INTO t(pad) VALUES (?)", [("x" * 100,) for _ in range(rows)])
    db.commit()
    db.close()


def test_backup_of_a_quiet_database(tmp_path):
    src, dst = str(tmp_path / "s.db"), str(tmp_path / "b.db")
    make(src, 50)
    backup(src, dst)
    c = sqlite3.connect(dst)
    assert c.execute("SELECT COUNT(*) FROM t").fetchone() == (50,)
    assert c.execute("PRAGMA integrity_check").fetchall() == [("ok",)]


def test_existing_destination_is_never_overwritten(tmp_path):
    src, dst = str(tmp_path / "s.db"), str(tmp_path / "b.db")
    make(src)
    open(dst, "wb").write(b"precious")
    with pytest.raises(FileExistsError):
        backup(src, dst)
    assert open(dst, "rb").read() == b"precious"


def test_uncommitted_work_of_another_connection_is_not_in_the_backup(tmp_path):
    src, dst = str(tmp_path / "s.db"), str(tmp_path / "b.db")
    make(src, 100)
    started, finish = threading.Event(), threading.Event()

    def writer():
        w = sqlite3.connect(src, timeout=10)
        w.execute("PRAGMA cache_size = 10")           # a tiny cache: pages of the open transaction spill into the file
        w.execute("BEGIN")
        for _ in range(3000):
            w.execute("INSERT INTO t(pad) VALUES (?)", ("y" * 100,))
        started.set()
        finish.wait(20)
        w.rollback()
        w.close()

    t = threading.Thread(target=writer)
    t.start()
    assert started.wait(20)
    timer = threading.Timer(1.0, finish.set)      # the writer ends its transaction (rollback) after one second
    timer.start()
    try:
        backup(src, dst)
    finally:
        finish.set()
        timer.cancel()
        t.join()
    c = sqlite3.connect(dst)
    try:
        check = c.execute("PRAGMA integrity_check").fetchall()
        count = c.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    except sqlite3.DatabaseError as exc:
        pytest.fail(f"The backup is corrupt ({exc}). Do not copy the file: use sqlite3's backup() API.")
    assert check == [("ok",)], f"integrity_check says {check}."
    assert count == 100, (f"The backup holds {count} rows but only 100 were committed: "
                          "it must contain a consistent snapshot of COMMITTED data only.")


def test_backup_while_another_connection_commits(tmp_path):
    src, dst = str(tmp_path / "s.db"), str(tmp_path / "b.db")
    make(src, 10)
    stop = threading.Event()

    def writer():
        w = sqlite3.connect(src, timeout=10)
        while not stop.is_set():
            w.execute("INSERT INTO t(pad) VALUES ('z')")
            w.commit()
        w.close()

    t = threading.Thread(target=writer)
    t.start()
    try:
        backup(src, dst)
    finally:
        stop.set()
        t.join()
    c = sqlite3.connect(dst)
    ids = [r[0] for r in c.execute("SELECT id FROM t ORDER BY id")]
    assert ids == list(range(1, len(ids) + 1)) and len(ids) >= 10, "A consistent snapshot has the ids 1..n without gaps."
    assert c.execute("PRAGMA integrity_check").fetchall() == [("ok",)]


def test_files_are_not_left_locked(tmp_path):
    src, dst = str(tmp_path / "s.db"), str(tmp_path / "b.db")
    make(src)
    backup(src, dst)
    os.remove(dst)                      # fails on Windows if the connection was left open
    os.remove(src)
