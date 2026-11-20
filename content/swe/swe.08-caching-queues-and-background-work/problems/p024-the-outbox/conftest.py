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





class FakeClock:
    """Time that moves only when a test says so. Call it to read the time: clock() -> seconds."""

    def __init__(self, start=0.0):
        self.t = float(start)

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += seconds
        return self.t



SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    queue        TEXT    NOT NULL DEFAULT 'default',
    kind         TEXT    NOT NULL,
    payload      TEXT    NOT NULL,
    dedupe_key   TEXT    UNIQUE,                       -- two enqueues with the same key make one job
    state        TEXT    NOT NULL DEFAULT 'queued' CHECK (state IN ('queued', 'running', 'done', 'dead')),
    attempts     INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 5,
    run_at       REAL    NOT NULL,                     -- not before this time (delays and backoff)
    lease_until  REAL,                                 -- while running: the lease deadline
    worker       TEXT,                                 -- who holds the lease
    last_error   TEXT,
    created_at   REAL    NOT NULL,
    finished_at  REAL
);
CREATE INDEX IF NOT EXISTS jobs_ready ON jobs (queue, state, run_at);
"""


class JobQueue:
    def __init__(self, path: str, now=time.time):
        self.path, self.now = path, now
        with closing(self._connect()) as db:
            db.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)       # autocommit: each statement is atomic
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode = WAL")                                  # readers do not block the writer
        db.execute("PRAGMA busy_timeout = 10000")
        return db

    # ---- producer side
    def enqueue(self, kind, payload, **options) -> int:
        with closing(self._connect()) as db:
            return self.enqueue_in(db, kind, payload, **options)

    def enqueue_in(self, db, kind, payload, *, queue="default", delay=0.0, max_attempts=5, dedupe_key=None) -> int:
        """Enqueue using the CALLER's connection: the job commits or rolls back together with the caller's own data."""
        now = self.now()
        row = db.execute(
            "INSERT INTO jobs (queue, kind, payload, dedupe_key, max_attempts, run_at, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT (dedupe_key) DO NOTHING RETURNING id",
            (queue, kind, json.dumps(payload, sort_keys=True), dedupe_key, max_attempts, now + delay, now),
        ).fetchone()
        if row is not None:
            return row["id"]
        return db.execute("SELECT id FROM jobs WHERE dedupe_key = ?", (dedupe_key,)).fetchone()["id"]

    # ---- worker side
    def reserve(self, worker: str, *, queue="default", lease=30.0):
        """Atomically claim the next ready job, or return None."""
        now = self.now()
        with closing(self._connect()) as db:
            # a job whose lease expired after its last allowed attempt is given up on
            db.execute("UPDATE jobs SET state = 'dead', finished_at = ?, last_error = 'lease expired on the last attempt' "
                       "WHERE queue = ? AND state = 'running' AND lease_until <= ? AND attempts >= max_attempts",
                       (now, queue, now))
            row = db.execute(
                "UPDATE jobs SET state = 'running', attempts = attempts + 1, lease_until = ?, worker = ? "
                "WHERE id = (SELECT id FROM jobs WHERE queue = ? AND "
                "            ((state = 'queued' AND run_at <= ?) OR (state = 'running' AND lease_until <= ?)) "
                "            ORDER BY run_at, id LIMIT 1) "
                "RETURNING *",
                (now + lease, worker, queue, now, now),
            ).fetchone()
            return dict(row) if row else None

    def heartbeat(self, job_id, worker, lease=30.0) -> bool:
        """Extend the lease of a long job. False means we lost it."""
        with closing(self._connect()) as db:
            cur = db.execute("UPDATE jobs SET lease_until = ? WHERE id = ? AND worker = ? AND state = 'running'",
                             (self.now() + lease, job_id, worker))
            return cur.rowcount == 1

    def complete(self, job_id, worker) -> bool:
        with closing(self._connect()) as db:
            cur = db.execute("UPDATE jobs SET state = 'done', finished_at = ?, lease_until = NULL "
                             "WHERE id = ? AND worker = ? AND state = 'running'", (self.now(), job_id, worker))
            return cur.rowcount == 1                     # False: our lease had expired and someone else owns the job

    def fail(self, job, error, *, retry_in=0.0, permanent=False) -> bool:
        """Record a failure. The job is retried later, or buried in the dead state."""
        with closing(self._connect()) as db:
            if permanent or job["attempts"] >= job["max_attempts"]:
                cur = db.execute("UPDATE jobs SET state = 'dead', last_error = ?, finished_at = ?, lease_until = NULL "
                                 "WHERE id = ? AND worker = ? AND state = 'running'", (error, self.now(), job["id"], job["worker"]))
            else:
                cur = db.execute("UPDATE jobs SET state = 'queued', last_error = ?, run_at = ?, lease_until = NULL "
                                 "WHERE id = ? AND worker = ? AND state = 'running'",
                                 (error, self.now() + retry_in, job["id"], job["worker"]))
            return cur.rowcount == 1

    # ---- operators
    def requeue_dead(self, job_id) -> bool:
        with closing(self._connect()) as db:
            cur = db.execute("UPDATE jobs SET state = 'queued', attempts = 0, run_at = ?, finished_at = NULL "
                             "WHERE id = ? AND state = 'dead'", (self.now(), job_id))
            return cur.rowcount == 1

    def get(self, job_id):
        with closing(self._connect()) as db:
            row = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            return dict(row) if row else None

    def stats(self, queue="default") -> dict:
        now = self.now()
        with closing(self._connect()) as db:
            counts = {r["state"]: r["n"] for r in db.execute(
                "SELECT state, COUNT(*) AS n FROM jobs WHERE queue = ? GROUP BY state", (queue,))}
            oldest = db.execute("SELECT MIN(run_at) AS t FROM jobs WHERE queue = ? AND state = 'queued' AND run_at <= ?",
                                (queue, now)).fetchone()["t"]
        return {**{s: counts.get(s, 0) for s in ("queued", "running", "done", "dead")},
                "oldest_ready_age": round(now - oldest, 3) if oldest is not None else 0.0}


class ProviderTimeout(Exception):
    pass


class FakeMailProvider:
    """Stands in for an e-mail API. `outbox` is what recipients really received."""

    def __init__(self, honours_idempotency_keys=True):
        self.honours_keys = honours_idempotency_keys
        self.outbox, self._by_key = [], {}
        self.lose_next_response = False

    def send(self, to, subject, body, idempotency_key=None):
        if self.honours_keys and idempotency_key is not None and idempotency_key in self._by_key:
            return self._by_key[idempotency_key]                    # a repeat: do not send again
        message_id = f"msg-{len(self.outbox) + 1}"
        self.outbox.append({"id": message_id, "to": to, "subject": subject})
        if idempotency_key is not None:
            self._by_key[idempotency_key] = message_id
        if self.lose_next_response:
            self.lose_next_response = False
            raise ProviderTimeout("sent, but the response never arrived")
        return message_id


class Crash(BaseException):
    """Simulates the PROCESS DYING. It derives from BaseException so the worker's `except Exception` cannot catch it."""


class CrashAt:
    def __init__(self, point=None):
        self.point = point

    def hit(self, name):
        if name == self.point:
            self.point = None                                     # crash once
            raise Crash(name)




@pytest.fixture
def clock():
    return FakeClock(0.0)


@pytest.fixture
def queue(tmp_path, clock):
    """The chapter's JobQueue (section 9.2) in a file in a temporary folder, on the fake clock."""
    return JobQueue(str(tmp_path / "queue.db"), now=clock)


@pytest.fixture
def shop(tmp_path):
    """An autocommit connection to the shop database (a different file from the queue)."""
    db = sqlite3.connect(str(tmp_path / "shop.db"), isolation_level=None)
    yield db
    db.close()


@pytest.fixture
def crash_at():
    return CrashAt


@pytest.fixture
def crash_type():
    return Crash
