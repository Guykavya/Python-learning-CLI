"""Course helpers for this problem (copied from the chapter). The tests receive them as fixtures; your solution never imports this file."""
import sqlite3

import pytest

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS members (
    project_id INTEGER NOT NULL REFERENCES projects(id),
    user_id    INTEGER NOT NULL REFERENCES users(id),
    PRIMARY KEY (project_id, user_id));
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'todo',
    assignee_id INTEGER REFERENCES users(id),
    created_at TEXT NOT NULL,
    completed_at TEXT);
CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY, task_id INTEGER, action TEXT NOT NULL, at TEXT NOT NULL);
"""

SEED = """
INSERT INTO users (id, name, email) VALUES
  (1, 'Ana',    'ana@example.com'),
  (2, 'Ben',    'ben@example.com'),
  (3, 'Cy',     'cy@example.com'),
  (4, 'Bounce', 'bounce@example.com');
INSERT INTO projects (id, name) VALUES (1, 'Website'), (2, 'Other');
INSERT INTO members (project_id, user_id) VALUES (1, 1), (1, 2), (1, 4), (2, 3);
"""


@pytest.fixture
def conn():
    """An in-memory Taskboard database with the schema and the seed data (users 1, 2, 4 are members of project 1)."""
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA + SEED)
    yield connection
    connection.close()


@pytest.fixture
def db_path(tmp_path):
    """A database FILE with the schema and the seed data."""
    path = str(tmp_path / "taskboard.db")
    seed = sqlite3.connect(path)
    seed.executescript(SCHEMA + SEED)
    seed.close()
    return path


