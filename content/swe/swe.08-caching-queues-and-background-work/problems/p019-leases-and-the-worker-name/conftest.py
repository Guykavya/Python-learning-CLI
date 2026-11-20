"""Course helpers for this problem, copied from the chapter (swe.08). The tests receive them as fixtures.
Your solution never imports this file: everything it needs arrives as a function argument."""
import fnmatch
import json
import math
import random
import signal
import sqlite3
import threading
import time
from contextlib import closing

import pytest

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    kind         TEXT    NOT NULL,
    payload      TEXT    NOT NULL DEFAULT '{}',
    state        TEXT    NOT NULL DEFAULT 'queued' CHECK (state IN ('queued', 'running', 'done', 'dead')),
    attempts     INTEGER NOT NULL DEFAULT 0,
    run_at       REAL    NOT NULL DEFAULT 0,
    lease_until  REAL,
    worker       TEXT
);
"""


class SlowSelectConnection:
    """Wraps a sqlite3 connection. After every statement that starts with SELECT it waits 20 ms,
    like a busy server. Two workers that SELECT 'the next job' at the same time then both see the same row."""

    def __init__(self, inner):
        self._inner = inner

    def execute(self, sql, params=()):
        cursor = self._inner.execute(sql, params)
        if sql.lstrip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            time.sleep(0.02)
            return _ListCursor(rows, cursor)
        return cursor

    def __getattr__(self, name):
        return getattr(self._inner, name)


class _ListCursor:
    def __init__(self, rows, cursor):
        self._rows, self.rowcount, self.description = list(rows), cursor.rowcount, cursor.description

    def fetchone(self):
        return self._rows.pop(0) if self._rows else None

    def fetchall(self):
        rows, self._rows = self._rows, []
        return rows

    def __iter__(self):
        return iter(self.fetchall())


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "jobs.db")
    with closing(sqlite3.connect(path)) as db:
        db.executescript(SCHEMA)
    return path


@pytest.fixture
def connect(db_path):
    """connect() -> a new autocommit connection to the jobs database (one per worker). Closed after the test."""
    opened = []

    def make(slow=False):
        db = sqlite3.connect(db_path, timeout=10, isolation_level=None, check_same_thread=False)
        db.row_factory = sqlite3.Row
        opened.append(db)
        return SlowSelectConnection(db) if slow else db

    yield make
    for db in opened:
        db.close()


@pytest.fixture
def add_jobs(db_path):
    """add_jobs(n) inserts n queued jobs that are ready at time 0; returns their ids."""

    def add(n, kind="task"):
        with closing(sqlite3.connect(db_path, isolation_level=None)) as db:
            return [db.execute("INSERT INTO jobs (kind) VALUES (?)", (kind,)).lastrowid for _ in range(n)]

    return add
