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
        self.tasks = {}
        self.next_id = 1

    def add(self, task):
        task.id = self.next_id
        self.next_id += 1
        self.tasks[task.id] = copy.copy(task)               # a copy in: later changes to `task` are not stored
        return task

    def get(self, task_id):
        if task_id not in self.tasks:
            raise NotFound(f"task {task_id} not found")
        return copy.copy(self.tasks[task_id])               # a copy out: the caller cannot change the stored one

    def save(self, task):
        self.tasks[task.id] = copy.copy(task)

    def open_count_for(self, user_id):
        return sum(1 for t in self.tasks.values() if t.assignee_id == user_id and t.status != "done")

    def list_for_project(self, project_id, status=None):
        rows = sorted(self.tasks.values(), key=lambda t: t.id)
        return [copy.copy(t) for t in rows if t.project_id == project_id and (status is None or t.status == status)]
