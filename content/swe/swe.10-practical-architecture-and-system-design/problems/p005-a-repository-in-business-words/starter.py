from dataclasses import dataclass


class DomainError(Exception):
    pass


class NotFound(DomainError):
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


class SqliteTaskRepo:
    def __init__(self, conn):
        self.conn = conn

    # TODO: add, get, save, open_count_for, list_for_project (all SQL of the program lives here)
