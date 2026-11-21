import sqlite3
from dataclasses import dataclass

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


class NotFound(Exception):
    pass


@dataclass
class Task:
    id: int | None
    project_id: int
    title: str
    status: str
    assignee_id: int | None
    created_at: str
    completed_at: str | None = None


def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


# ---- the repositories (given: see problem p005) -------------------------------------------------------------
def _task(row):
    return Task(id=row["id"], project_id=row["project_id"], title=row["title"], status=row["status"],
                assignee_id=row["assignee_id"], created_at=row["created_at"], completed_at=row["completed_at"])


class SqliteTaskRepo:
    def __init__(self, conn):
        self.conn = conn

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

    def list_for_project(self, project_id, status=None):
        sql, args = "SELECT * FROM tasks WHERE project_id = ?", [project_id]
        if status is not None:
            sql, args = sql + " AND status = ?", args + [status]
        return [_task(r) for r in self.conn.execute(sql + " ORDER BY id", args).fetchall()]

    def add_audit(self, task_id, action, at):
        self.conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, ?, ?)", (task_id, action, at))

    def audit_for(self, task_id):
        return [r["action"] for r in self.conn.execute("SELECT action FROM audit WHERE task_id = ? ORDER BY id", (task_id,))]


class SqliteProjectRepo:
    def __init__(self, conn):
        self.conn = conn

    def exists(self, project_id):
        return self.conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is not None

    def is_member(self, project_id, user_id):
        return self.conn.execute("SELECT 1 FROM members WHERE project_id = ? AND user_id = ?", (project_id, user_id)).fetchone() is not None


class SqliteUserRepo:
    def __init__(self, conn):
        self.conn = conn

    def email_of(self, user_id):
        return self.conn.execute("SELECT email FROM users WHERE id = ?", (user_id,)).fetchone()[0]


class SqliteRepos:
    """The bundle: every repository on the SAME connection."""

    def __init__(self, conn):
        self.tasks = SqliteTaskRepo(conn)
        self.projects = SqliteProjectRepo(conn)
        self.users = SqliteUserRepo(conn)


# ---- the unit of work (yours) ---------------------------------------------------------------------------------
class SqliteUnitOfWork:
    def __init__(self, path):
        self.path = path

    # TODO: __enter__, __exit__, commit
