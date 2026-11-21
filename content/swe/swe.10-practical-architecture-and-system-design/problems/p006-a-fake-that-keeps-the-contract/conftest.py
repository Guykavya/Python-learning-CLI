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


@pytest.fixture
def sqlite_repo(conn):
    """The real repository of problem p005 (its reference solution), working on the seeded in-memory database."""
    from solution import NotFound, Task

    def _task(row):
        return Task(id=row["id"], project_id=row["project_id"], title=row["title"], status=row["status"],
                    assignee_id=row["assignee_id"], created_at=row["created_at"], completed_at=row["completed_at"])

    class SqliteTaskRepo:
        def __init__(self, c):
            self.conn = c

        def add(self, task):
            cur = self.conn.execute(
                "INSERT INTO tasks (project_id, title, status, assignee_id, created_at, completed_at) VALUES (?, ?, ?, ?, ?, ?)",
                (task.project_id, task.title, task.status, task.assignee_id, task.created_at, task.completed_at))
            task.id = cur.lastrowid
            return task

        def get(self, task_id):
            row = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if row is None:
                raise NotFound(f"task {task_id} not found")
            return _task(row)

        def save(self, task):
            self.conn.execute("UPDATE tasks SET title = ?, status = ?, assignee_id = ?, completed_at = ? WHERE id = ?",
                              (task.title, task.status, task.assignee_id, task.completed_at, task.id))

        def open_count_for(self, user_id):
            return self.conn.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id = ? AND status != 'done'", (user_id,)).fetchone()[0]

        def list_for_project(self, project_id, status=None):
            sql, args = "SELECT * FROM tasks WHERE project_id = ?", [project_id]
            if status is not None:
                sql, args = sql + " AND status = ?", args + [status]
            return [_task(r) for r in self.conn.execute(sql + " ORDER BY id", args).fetchall()]

    return SqliteTaskRepo(conn)
