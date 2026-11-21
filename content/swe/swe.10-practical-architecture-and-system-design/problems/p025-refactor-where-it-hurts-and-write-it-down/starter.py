import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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

MAX_OPEN = 3
ALLOWED = {("todo", "doing"), ("doing", "todo"), ("doing", "done"), ("done", "todo")}


# ---- domain errors (given) -----------------------------------------------------------------------------------
class DomainError(Exception):
    """A business rule was broken. This is a normal outcome, not a bug."""


class NotFound(DomainError):
    pass


class InvalidInput(DomainError):
    pass


class RuleViolation(DomainError):
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


# ---- the layers you will build (stubs) ----------------------------------------------------------------------
class SqliteUnitOfWork:
    def __init__(self, path):
        self.path = path

    # TODO: __enter__ (open a connection, build the repositories), __exit__ (rollback, close), commit


def create_task(uow, mailer, project_id, title, assignee_id=None):
    raise NotImplementedError


def update_task(uow, mailer, task_id, assignee_id=None, status=None):
    raise NotImplementedError


def get_task(uow, task_id):
    raise NotImplementedError


def list_tasks(uow, project_id, status=None):
    raise NotImplementedError


ADR = ""            # TODO: an architecture decision record (Status, Context, Decision, Consequences, Alternatives)
PAIN_LOG = []       # TODO: [{"pain": ..., "evidence": ..., "remedy": "service layer" | "repository" | "unit of work"}, ...]


# ---- the application as it is today: everything in the routes (chapter 2.2) -------------------------------------
def create_app(db_path, mailer):
    app = FastAPI(title="Taskboard")
    state = {"conn": None}

    def get_conn():
        """One shared connection for the whole app (simple, and a trap: chapter 3)."""
        if state["conn"] is None:
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.executescript(SCHEMA)
            state["conn"] = conn
        return state["conn"]

    class NewTask(BaseModel):
        title: str
        assignee_id: int | None = None

    class TaskPatch(BaseModel):
        assignee_id: int | None = None
        status: str | None = None

    def now():
        return datetime.now(timezone.utc).isoformat()

    def task_json(conn, task_id):
        t = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return {"id": t["id"], "project_id": t["project_id"], "title": t["title"], "status": t["status"],
                "assignee_id": t["assignee_id"], "completed_at": t["completed_at"]}

    @app.post("/projects/{project_id}/tasks", status_code=201)
    def create(project_id: int, body: NewTask):
        conn = get_conn()
        title = body.title.strip()
        if not title or len(title) > 120:
            raise HTTPException(422, "title must have 1 to 120 characters")
        if conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
            raise HTTPException(404, "project not found")
        if body.assignee_id is not None:
            member = conn.execute("SELECT 1 FROM members WHERE project_id = ? AND user_id = ?",
                                  (project_id, body.assignee_id)).fetchone()
            if member is None:
                raise HTTPException(409, "assignee is not a member of this project")
            open_count = conn.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id = ? AND status != 'done'",
                                      (body.assignee_id,)).fetchone()[0]
            if open_count >= MAX_OPEN:
                raise HTTPException(409, f"assignee already has {MAX_OPEN} open tasks")
        stamp = now()
        cur = conn.execute("INSERT INTO tasks (project_id, title, status, assignee_id, created_at) VALUES (?, ?, 'todo', ?, ?)",
                           (project_id, title, body.assignee_id, stamp))
        task_id = cur.lastrowid
        conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, 'created', ?)", (task_id, stamp))
        if body.assignee_id is not None:
            email = conn.execute("SELECT email FROM users WHERE id = ?", (body.assignee_id,)).fetchone()[0]
            mailer.send_email(email, f"New task: {title}")
        conn.commit()
        return {"id": task_id, "title": title, "status": "todo", "assignee_id": body.assignee_id}

    @app.patch("/tasks/{task_id}")
    def update(task_id: int, body: TaskPatch):
        conn = get_conn()
        task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if task is None:
            raise HTTPException(404, "task not found")
        stamp = now()
        if body.assignee_id is not None:
            member = conn.execute("SELECT 1 FROM members WHERE project_id = ? AND user_id = ?",
                                  (task["project_id"], body.assignee_id)).fetchone()
            if member is None:
                raise HTTPException(409, "assignee is not a member of this project")
            conn.execute("UPDATE tasks SET assignee_id = ? WHERE id = ?", (body.assignee_id, task_id))
            conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, 'assigned', ?)", (task_id, stamp))
            email = conn.execute("SELECT email FROM users WHERE id = ?", (body.assignee_id,)).fetchone()[0]
            mailer.send_email(email, f"Task assigned: {task['title']}")
        if body.status is not None:
            if (task["status"], body.status) not in ALLOWED:
                raise HTTPException(409, f"cannot move from {task['status']} to {body.status}")
            completed = stamp if body.status == "done" else None
            conn.execute("UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?", (body.status, completed, task_id))
            conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, ?, ?)", (task_id, f"status:{body.status}", stamp))
        conn.commit()
        return task_json(conn, task_id)

    @app.get("/tasks/{task_id}")
    def read(task_id: int):
        conn = get_conn()
        if conn.execute("SELECT 1 FROM tasks WHERE id = ?", (task_id,)).fetchone() is None:
            raise HTTPException(404, "task not found")
        return task_json(conn, task_id)

    @app.get("/projects/{project_id}/tasks")
    def listing(project_id: int, status: str | None = None):
        conn = get_conn()
        sql, args = "SELECT id FROM tasks WHERE project_id = ?", [project_id]
        if status is not None:
            sql, args = sql + " AND status = ?", args + [status]
        ids = [r["id"] for r in conn.execute(sql + " ORDER BY id", args)]
        return [task_json(conn, i) for i in ids]

    return app
