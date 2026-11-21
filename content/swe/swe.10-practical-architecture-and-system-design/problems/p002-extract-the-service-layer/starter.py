import sqlite3

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
    # TODO: the rules of problem.md, written without any HTTP and without commit()
    raise NotImplementedError


STATUS_FOR = {NotFound: 404, InvalidInput: 422, RuleViolation: 409}


class NewTask(BaseModel):
    title: str
    assignee_id: int | None = None


def create_app(db_path, mailer):
    """The thin web layer: it translates. Given; do not change it."""
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
