import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import JSONResponse
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


# ---- layer 3 (infrastructure): the only place with SQL -------------------------------------------------------
def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


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
            raise NotFound("task not found")
        return _task(row)

    def save(self, task):
        self.conn.execute("UPDATE tasks SET title = ?, status = ?, assignee_id = ?, completed_at = ? WHERE id = ?",
                          (task.title, task.status, task.assignee_id, task.completed_at, task.id))

    def list_for_project(self, project_id, status=None):
        sql, args = "SELECT * FROM tasks WHERE project_id = ?", [project_id]
        if status is not None:
            sql, args = sql + " AND status = ?", args + [status]
        return [_task(r) for r in self.conn.execute(sql + " ORDER BY id", args).fetchall()]

    def open_count_for(self, user_id):
        return self.conn.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id = ? AND status != 'done'", (user_id,)).fetchone()[0]

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


class SqliteUnitOfWork:
    """One connection and one transaction per use case."""

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.conn = connect(self.path)
        self.tasks, self.projects, self.users = SqliteTaskRepo(self.conn), SqliteProjectRepo(self.conn), SqliteUserRepo(self.conn)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.rollback()                       # a no-op after commit(); undoes everything otherwise
        self.conn.close()

    def commit(self):
        self.conn.commit()


# ---- layer 1 (use cases): the rules, written once ---------------------------------------------------------------
def _now():
    return datetime.now(timezone.utc).isoformat()


def _check_member(uow, project_id, user_id):
    if not uow.projects.is_member(project_id, user_id):
        raise RuleViolation("assignee is not a member of this project")


def _check_capacity(uow, user_id):
    """Rule 3, written exactly once."""
    if uow.tasks.open_count_for(user_id) >= MAX_OPEN:
        raise RuleViolation(f"assignee already has {MAX_OPEN} open tasks")


def create_task(uow, mailer, project_id, title, assignee_id=None):
    title = title.strip()
    if not title or len(title) > 120:
        raise InvalidInput("title must have 1 to 120 characters")
    with uow:
        if not uow.projects.exists(project_id):
            raise NotFound("project not found")
        if assignee_id is not None:
            _check_member(uow, project_id, assignee_id)
            _check_capacity(uow, assignee_id)
        task = uow.tasks.add(Task(None, project_id, title, "todo", assignee_id, _now()))
        uow.tasks.add_audit(task.id, "created", task.created_at)
        if assignee_id is not None:
            mailer.send_email(uow.users.email_of(assignee_id), f"New task: {title}")
        uow.commit()
        return task


def update_task(uow, mailer, task_id, assignee_id=None, status=None):
    with uow:
        task = uow.tasks.get(task_id)
        stamp = _now()
        if assignee_id is not None:
            _check_member(uow, task.project_id, assignee_id)
            if task.status != "done" and assignee_id != task.assignee_id:
                _check_capacity(uow, assignee_id)              # an open task moving to a new person
            task.assignee_id = assignee_id
            uow.tasks.add_audit(task.id, "assigned", stamp)
            mailer.send_email(uow.users.email_of(assignee_id), f"Task assigned: {task.title}")
        if status is not None:
            if (task.status, status) not in ALLOWED:
                raise RuleViolation(f"cannot move from {task.status} to {status}")
            if task.status == "done" and task.assignee_id is not None:
                _check_capacity(uow, task.assignee_id)         # reopening makes the task open again
            task.status = status
            task.completed_at = stamp if status == "done" else None
            uow.tasks.add_audit(task.id, f"status:{status}", stamp)
        uow.tasks.save(task)
        uow.commit()
        return task


def get_task(uow, task_id):
    with uow:
        return uow.tasks.get(task_id)


def list_tasks(uow, project_id, status=None):
    with uow:
        return uow.tasks.list_for_project(project_id, status)


# ---- the web layer: it only translates --------------------------------------------------------------------------
STATUS_FOR = {NotFound: 404, InvalidInput: 422, RuleViolation: 409}


class NewTask(BaseModel):
    title: str
    assignee_id: int | None = None


class TaskPatch(BaseModel):
    assignee_id: int | None = None
    status: str | None = None


def task_json(t):
    return {"id": t.id, "project_id": t.project_id, "title": t.title, "status": t.status,
            "assignee_id": t.assignee_id, "completed_at": t.completed_at}


def create_app(db_path, mailer):
    """The composition root: the only place that chooses concrete implementations."""
    app = FastAPI(title="Taskboard")

    @app.exception_handler(DomainError)
    def domain_error_to_http(request, exc):
        return JSONResponse({"detail": str(exc)}, status_code=STATUS_FOR.get(type(exc), 400))

    def new_uow():
        return SqliteUnitOfWork(db_path)

    @app.post("/projects/{project_id}/tasks", status_code=201)
    def create(project_id: int, body: NewTask):
        return task_json(create_task(new_uow(), mailer, project_id, body.title, body.assignee_id))

    @app.patch("/tasks/{task_id}")
    def update(task_id: int, body: TaskPatch):
        return task_json(update_task(new_uow(), mailer, task_id, body.assignee_id, body.status))

    @app.get("/tasks/{task_id}")
    def read(task_id: int):
        return task_json(get_task(new_uow(), task_id))

    @app.get("/projects/{project_id}/tasks")
    def listing(project_id: int, status: str | None = None):
        return [task_json(t) for t in list_tasks(new_uow(), project_id, status)]

    return app


# ---- the documents -----------------------------------------------------------------------------------------------
ADR = """# ADR 0001: One use case, one unit of work, one place for each rule

## Status
Accepted

## Context
Rule 3 (at most 3 open tasks) was enforced in 1 of 3 entry points: assigning by PATCH and reopening a done task silently skipped it
(test_assign_by_patch_respects_wip_limit and test_reopen_respects_wip_limit failed). All requests shared one SQLite connection: a request
that failed after an insert left it pending and the next successful request committed it (test_failed_email_leaves_no_half_saved_task).
Routes held rules, SQL, e-mail and JSON in one block, so checking a single rule needed HTTP and a database.

## Decision
Use cases live in service functions (create_task, update_task) that raise domain errors and know nothing about HTTP. All SQL lives in
repository classes. Every request gets its own SqliteUnitOfWork (own connection, own transaction): the service calls commit() once, and
leaving the block always rolls back whatever was not committed. The routes only translate: parse, call, map DomainError to a status code.

## Consequences
+ The rule exists once, a failed request cannot affect another, and the rules run in unit tests with a fake unit of work in milliseconds.
- More files and names, and a mapping from rows to Task objects; services must remember to call commit().
- E-mail is still sent inside the transaction: a rolled-back change can still e-mail (the outbox of chapter 9 would fix this when it hurts).

## Alternatives
- Keep the routes and copy the check into the two forgotten places: fixes today's bug, not the next copy.
- A domain model with rules on Task: not needed yet, the rules are few and the service holds them in one place.
- Separate services: no second team and no different scaling need; stay a modular monolith.
"""

PAIN_LOG = [
    {"pain": "Rule 3 (max 3 open tasks) enforced in 1 of 3 entry points",
     "evidence": "test_assign_by_patch_respects_wip_limit and test_reopen_respects_wip_limit failed on the monolith",
     "remedy": "service layer"},
    {"pain": "Rules, SQL, e-mail and JSON mixed in the same route handlers",
     "evidence": "16 conn.execute calls inside create_app; testing a rule needs HTTP and a database",
     "remedy": "repository"},
    {"pain": "A failed request left a half-saved task that the next request committed",
     "evidence": "test_failed_email_leaves_no_half_saved_task failed: ['for bounce', 'next'] != ['next']",
     "remedy": "unit of work"},
]
