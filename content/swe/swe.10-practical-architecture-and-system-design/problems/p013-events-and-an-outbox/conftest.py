"""Course helpers for this problem (copied from the chapter). The tests receive them as fixtures; your solution never imports this file."""
import copy
from dataclasses import dataclass

import pytest

NOW = "2026-01-01T00:00:00"


@dataclass
class OutboxItem:
    id: int
    kind: str
    payload: dict


@pytest.fixture
def world():
    """A transactional in-memory world (chapter 7.3 and 9.4): the store survives between units of work; a unit of work
    works on a private copy that replaces the store only on commit(). Built on the Task and NotFound of your solution."""
    from solution import NotFound, Task

    class FakeStore:
        def __init__(self):
            self.data = {"tasks": {}, "outbox": [], "next_task_id": 1, "members": {(1, 1), (1, 2), (1, 4), (2, 3)}}
            self.fail_next_commit = False

    class TaskRepo:
        def __init__(self, data):
            self.data = data

        def get(self, task_id):
            if task_id not in self.data["tasks"]:
                raise NotFound(f"task {task_id} not found")
            return copy.copy(self.data["tasks"][task_id])

        def save(self, task):
            self.data["tasks"][task.id] = copy.copy(task)

        def open_count_for(self, user_id):
            return sum(1 for t in self.data["tasks"].values() if t.assignee_id == user_id and t.status != "done")

    class ProjectRepo:
        def __init__(self, data):
            self.data = data

        def is_member(self, project_id, user_id):
            return (project_id, user_id) in self.data["members"]

    class OutboxRepo:
        def __init__(self, data):
            self.data = data

        def add(self, kind, payload, at):
            rows = self.data["outbox"]
            rows.append({"id": len(rows) + 1, "kind": kind, "payload": copy.deepcopy(payload), "created_at": at, "sent_at": None})

        def pending(self, limit=50):
            rows = [r for r in self.data["outbox"] if r["sent_at"] is None][:limit]
            return [OutboxItem(r["id"], r["kind"], copy.deepcopy(r["payload"])) for r in rows]

        def mark_sent(self, item_id, at):
            for r in self.data["outbox"]:
                if r["id"] == item_id:
                    r["sent_at"] = at

    class FakeUnitOfWork:
        def __init__(self, store):
            self.store = store

        def __enter__(self):
            self.work = copy.deepcopy(self.store.data)           # a private copy = our transaction
            self.tasks, self.projects, self.outbox = TaskRepo(self.work), ProjectRepo(self.work), OutboxRepo(self.work)
            return self

        def __exit__(self, exc_type, exc, tb):
            pass                                                  # not committed -> the copy is simply dropped

        def commit(self):
            if self.store.fail_next_commit:
                self.store.fail_next_commit = False
                raise RuntimeError("disk full")                   # the commit itself fails: nothing is applied
            self.store.data = self.work

    class World:
        def __init__(self):
            self.store = FakeStore()

        def uow(self):
            return FakeUnitOfWork(self.store)

        def add_task(self, title="x", project_id=1, status="todo", assignee_id=None):
            data = self.store.data
            task = Task(data["next_task_id"], project_id, title, status, assignee_id, NOW)
            data["tasks"][task.id] = task
            data["next_task_id"] += 1
            return task.id

        def task(self, task_id):
            return copy.copy(self.store.data["tasks"][task_id])

        def pending(self):
            with self.uow() as uow:
                return [(i.kind, i.payload) for i in uow.outbox.pending(1000)]

        def sent_at(self):
            return [r["sent_at"] for r in self.store.data["outbox"]]

    return World()


