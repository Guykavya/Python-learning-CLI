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
        with closing(self._connect()) as db:
            db.executescript(SCHEMA)

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        return db

    def enqueue(self, kind, payload, *, delay=0.0, max_attempts=5, dedupe_key=None):
        now = self.now()
        with closing(self._connect()) as db:
            row = db.execute(
                "INSERT INTO jobs (kind, payload, dedupe_key, max_attempts, run_at, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT (dedupe_key) DO NOTHING RETURNING id",
                (kind, json.dumps(payload, sort_keys=True), dedupe_key, max_attempts, now + delay, now),
            ).fetchone()
            if row is not None:
                return row["id"]
            return db.execute("SELECT id FROM jobs WHERE dedupe_key = ?", (dedupe_key,)).fetchone()["id"]

    def reserve(self, worker, *, lease=30.0):
        now = self.now()
        with closing(self._connect()) as db:
            row = db.execute(
                "UPDATE jobs SET state = 'running', attempts = attempts + 1, lease_until = ?, worker = ? "
                "WHERE id = (SELECT id FROM jobs WHERE "
                "            (state = 'queued' AND run_at <= ?) OR (state = 'running' AND lease_until <= ?) "
                "            ORDER BY run_at, id LIMIT 1) "
                "RETURNING *",
                (now + lease, worker, now, now),
            ).fetchone()
            return dict(row) if row else None

    def complete(self, job_id, worker):
        with closing(self._connect()) as db:
            cur = db.execute("UPDATE jobs SET state = 'done', finished_at = ?, lease_until = NULL "
                             "WHERE id = ? AND worker = ? AND state = 'running'", (self.now(), job_id, worker))
            return cur.rowcount == 1

    def fail(self, job, error, *, retry_in=0.0, permanent=False):
        with closing(self._connect()) as db:
            if permanent or job["attempts"] >= job["max_attempts"]:
                cur = db.execute("UPDATE jobs SET state = 'dead', last_error = ?, finished_at = ?, lease_until = NULL "
                                 "WHERE id = ? AND worker = ? AND state = 'running'",
                                 (error, self.now(), job["id"], job["worker"]))
            else:
                cur = db.execute("UPDATE jobs SET state = 'queued', last_error = ?, run_at = ?, lease_until = NULL "
                                 "WHERE id = ? AND worker = ? AND state = 'running'",
                                 (error, self.now() + retry_in, job["id"], job["worker"]))
            return cur.rowcount == 1

    def get(self, job_id):
        with closing(self._connect()) as db:
            row = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            return dict(row) if row else None
