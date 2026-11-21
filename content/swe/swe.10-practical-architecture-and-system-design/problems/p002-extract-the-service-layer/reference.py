import sqlite3
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

MAX_OPEN = 3


class DomainError(Exception):
    """A business rule was broken. This is a normal outcome, not a bug."""


class NotFound(DomainError):
    pass


class InvalidInput(DomainError):
    pass


class RuleViolation(DomainError):
    pass


def create_task(conn, mailer, project_id, title, assignee_id=None):
    title = title.strip()
    if not title or len(title) > 120:
        raise InvalidInput("title must have 1 to 120 characters")
    if conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
        raise NotFound("project not found")
    if assignee_id is not None:
        member = conn.execute("SELECT 1 FROM members WHERE project_id = ? AND user_id = ?",
                              (project_id, assignee_id)).fetchone()
        if member is None:
            raise RuleViolation("assignee is not a member of this project")
        open_count = conn.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id = ? AND status != 'done'",
                                  (assignee_id,)).fetchone()[0]
        if open_count >= MAX_OPEN:
            raise RuleViolation(f"assignee already has {MAX_OPEN} open tasks")
    stamp = datetime.now(timezone.utc).isoformat()
    cur = conn.execute("INSERT INTO tasks (project_id, title, status, assignee_id, created_at) VALUES (?, ?, 'todo', ?, ?)",
                       (project_id, title, assignee_id, stamp))
    task_id = cur.lastrowid
    conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, 'created', ?)", (task_id, stamp))
    if assignee_id is not None:
        email = conn.execute("SELECT email FROM users WHERE id = ?", (assignee_id,)).fetchone()[0]
        mailer.send_email(email, f"New task: {title}")
    return {"id": task_id, "title": title, "status": "todo", "assignee_id": assignee_id}


STATUS_FOR = {NotFound: 404, InvalidInput: 422, RuleViolation: 409}


class NewTask(BaseModel):
    title: str
    assignee_id: int | None = None


def create_app(db_path, mailer):
    """The thin web layer: it translates."""
    app = FastAPI(title="Taskboard")

    @app.exception_handler(DomainError)
    def domain_error_to_http(request, exc):
        return JSONResponse({"detail": str(exc)}, status_code=STATUS_FOR.get(type(exc), 400))

    @app.post("/projects/{project_id}/tasks", status_code=201)
    def create(project_id: int, body: NewTask):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            result = create_task(conn, mailer, project_id, body.title, body.assignee_id)
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    return app
