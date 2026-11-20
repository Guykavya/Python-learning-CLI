import sqlite3

import pytest

from solution import run_in_transaction


class FakeDb:
    def __init__(self, log):
        self.log = log

    def commit(self):
        self.log.append("commit")

    def rollback(self):
        self.log.append("rollback")

    def close(self):
        self.log.append("close")


def setup():
    log = []
    return log, (lambda: FakeDb(log))


LOCKED = sqlite3.OperationalError("database is locked")


def test_success_first_time():
    log, connect = setup()
    assert run_in_transaction(connect, lambda db: 42, sleep=lambda s: None) == 42
    assert log == ["commit", "close"], f"One attempt: commit, then close. Got {log}."


def test_retries_a_locked_database_with_backoff():
    log, connect = setup()
    waits, calls = [], []

    def work(db):
        calls.append(1)
        if len(calls) < 3:
            raise LOCKED
        return "done"

    assert run_in_transaction(connect, work, attempts=5, sleep=waits.append) == "done"
    assert len(calls) == 3 and waits == [0.05, 0.1], f"Two failures: sleeps 0.05 and 0.1; got {waits}."
    assert log == ["rollback", "close", "rollback", "close", "commit", "close"], (
        f"Roll back and close after each failed attempt, commit on success. Got {log}.")


def test_gives_up_after_the_last_attempt():
    log, connect = setup()
    waits, calls = [], []

    def work(db):
        calls.append(1)
        raise LOCKED

    with pytest.raises(sqlite3.OperationalError, match="locked"):
        run_in_transaction(connect, work, attempts=3, sleep=waits.append)
    assert len(calls) == 3, "attempts=3 means three runs of work."
    assert waits == [0.05, 0.1], "No sleep after the last attempt."
    assert "commit" not in log


@pytest.mark.parametrize("error", [ValueError("bad data"), sqlite3.IntegrityError("UNIQUE constraint failed: t.x"),
                                   sqlite3.OperationalError("no such table: t"), KeyError("k")])
def test_other_errors_are_not_retried(error):
    log, connect = setup()
    waits, calls = [], []

    def work(db):
        calls.append(1)
        raise error

    with pytest.raises(type(error)):
        run_in_transaction(connect, work, sleep=waits.append)
    assert len(calls) == 1 and waits == [], f"{error!r} must be raised at once, without a retry or a sleep."
    assert log == ["rollback", "close"]


def test_work_is_never_repeated_after_a_commit():
    log, connect = setup()
    calls = []

    class Db(FakeDb):
        def close(self):
            super().close()
            raise sqlite3.OperationalError("database is locked")     # even a strange error after the commit

    def work(db):
        calls.append(1)
        return "ok"

    try:
        run_in_transaction(lambda: Db(log), work, sleep=lambda s: None)
    except sqlite3.OperationalError:
        pass
    assert len(calls) == 1 and log.count("commit") == 1, "After a successful commit the work must not run again."


def test_a_new_connection_for_every_attempt():
    made = []

    def connect():
        made.append(1)
        return FakeDb([])

    state = []

    def work(db):
        state.append(1)
        if len(state) == 1:
            raise LOCKED

    run_in_transaction(connect, work, sleep=lambda s: None)
    assert len(made) == 2, "Open a fresh connection for each attempt."


def test_with_real_sqlite_and_a_blocking_writer(tmp_path):
    path = str(tmp_path / "x.db")
    setup_db = sqlite3.connect(path)
    setup_db.execute("CREATE TABLE t (x INTEGER)")
    setup_db.commit()
    blocker = sqlite3.connect(path)
    blocker.execute("BEGIN IMMEDIATE")
    waits = []

    def sleep(seconds):
        waits.append(seconds)
        if len(waits) == 2:
            blocker.rollback()                    # the lock disappears while we back off

    def connect():
        return sqlite3.connect(path, timeout=0.05)

    run_in_transaction(connect, lambda db: db.execute("INSERT INTO t VALUES (1)"), attempts=5, sleep=sleep)
    assert len(waits) == 2
    assert setup_db.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1
