import json
import sqlite3
import time
from contextlib import closing

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    kind         TEXT    NOT NULL,
    payload      TEXT    NOT NULL,
    dedupe_key   TEXT    UNIQUE,
    state        TEXT    NOT NULL DEFAULT 'queued' CHECK (state IN ('queued', 'running', 'done', 'dead')),
    attempts     INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 5,
    run_at       REAL    NOT NULL,
    lease_until  REAL,
    worker       TEXT,
    last_error   TEXT,
    created_at   REAL    NOT NULL,
    finished_at  REAL
);
"""


class JobQueue:
    def __init__(self, path, now=time.time):
        self.path, self.now = path, now
        # TODO: create the table

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        return db

    def enqueue(self, kind, payload, *, delay=0.0, max_attempts=5, dedupe_key=None):
        return 0

    def reserve(self, worker, *, lease=30.0):
        return None

    def complete(self, job_id, worker):
        return False

    def fail(self, job, error, *, retry_in=0.0, permanent=False):
        return False

    def get(self, job_id):
        return None
