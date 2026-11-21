import copy
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


class FakeTaskRepo:
    """An in-memory repository with the same interface as the SQLite one."""

    def __init__(self):
        self.tasks = {}                     # id -> Task (a private copy)
        self.next_id = 1

    # TODO: add, get, save, open_count_for, list_for_project. Copy in and out.
