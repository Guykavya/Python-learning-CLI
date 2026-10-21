"""SQLite tracker. One file: data/progress.db. No server, no port."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime

from learn import paths

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- one row per day you actually studied; the day count is COUNT(*)
CREATE TABLE IF NOT EXISTS active_days (
    day TEXT PRIMARY KEY,
    seconds INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS problem_state (
    problem_id      TEXT PRIMARY KEY,
    status          TEXT NOT NULL DEFAULT 'started',   -- started | solved
    first_started   TEXT,
    session_started TEXT,
    session_dir     TEXT,
    is_review       INTEGER NOT NULL DEFAULT 0,
    hints_used      INTEGER NOT NULL DEFAULT 0,        -- hints in the current session
    solution_viewed INTEGER NOT NULL DEFAULT 0,        -- in the current session
    failed_checks   INTEGER NOT NULL DEFAULT 0,        -- in the current session
    seconds_spent   INTEGER NOT NULL DEFAULT 0,        -- all sessions together
    solved_at       TEXT,
    best_quality    REAL,
    last_quality    REAL,
    review_due      TEXT,
    review_interval REAL,
    reviews_done    INTEGER NOT NULL DEFAULT 0,
    difficulty      REAL
);

CREATE TABLE IF NOT EXISTS attempts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id   TEXT NOT NULL,
    at           TEXT NOT NULL,
    passed       INTEGER NOT NULL,
    tests_passed INTEGER,
    tests_total  INTEGER,
    seconds      INTEGER,
    hints_used   INTEGER,
    is_review    INTEGER NOT NULL DEFAULT 0,
    quality      REAL
);

CREATE TABLE IF NOT EXISTS events (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    at     TEXT NOT NULL,
    kind   TEXT NOT NULL,
    ref    TEXT,
    detail TEXT
);

CREATE TABLE IF NOT EXISTS ratings (
    track  TEXT PRIMARY KEY,
    rating REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS track_cursor (
    track     TEXT PRIMARY KEY,
    module_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS external_solves (
    site        TEXT NOT NULL,       -- leetcode | codeforces | cses
    problem_key TEXT NOT NULL,       -- slug, 1520A, task id
    title       TEXT,
    url         TEXT,
    tags        TEXT,                -- comma separated
    difficulty  TEXT,
    modules     TEXT,                -- comma separated dsa module ids
    solved_at   TEXT,
    attempts    INTEGER,
    minutes     INTEGER,
    hints       INTEGER,
    insight     TEXT,
    code_path   TEXT,
    source      TEXT,                -- sync | log
    PRIMARY KEY (site, problem_key)
);

CREATE TABLE IF NOT EXISTS external_stats (
    site       TEXT PRIMARY KEY,
    fetched_at TEXT,
    summary    TEXT
);

CREATE TABLE IF NOT EXISTS playground_files (
    path       TEXT PRIMARY KEY,
    hash       TEXT NOT NULL,
    scanned_at TEXT NOT NULL,
    features   TEXT NOT NULL,         -- comma separated feature names
    modules    TEXT NOT NULL          -- comma separated module ids
);

CREATE TABLE IF NOT EXISTS playground_activity (
    day       TEXT NOT NULL,
    module_id TEXT NOT NULL,
    files     INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (day, module_id)
);
"""


def now() -> str:
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def today() -> str:
    return date.today().isoformat()


def connect() -> sqlite3.Connection:
    path = paths.db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def log_event(conn: sqlite3.Connection, kind: str, ref: str | None = None, detail: str | None = None) -> None:
    conn.execute("INSERT INTO events(at, kind, ref, detail) VALUES (?, ?, ?, ?)", (now(), kind, ref, detail))


def mark_active(conn: sqlite3.Connection, seconds: int = 0) -> None:
    conn.execute(
        "INSERT INTO active_days(day, seconds) VALUES (?, ?) "
        "ON CONFLICT(day) DO UPDATE SET seconds = seconds + excluded.seconds",
        (today(), max(0, seconds)),
    )


def day_count(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM active_days").fetchone()[0]


def get_meta(conn: sqlite3.Connection, key: str, default: str | None = None) -> str | None:
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row[0] if row else default


def set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO meta(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def problem_state(conn: sqlite3.Connection, problem_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM problem_state WHERE problem_id = ?", (problem_id,)).fetchone()


def states(conn: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    return {r["problem_id"]: r for r in conn.execute("SELECT * FROM problem_state")}
