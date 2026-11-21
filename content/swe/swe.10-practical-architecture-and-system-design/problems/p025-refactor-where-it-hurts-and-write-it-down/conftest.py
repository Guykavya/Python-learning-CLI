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




class MailError(Exception):
    pass


class RecordingMailer:
    """Records what was 'sent'. Refuses addresses that start with 'bounce', so tests can make delivery fail."""

    def __init__(self):
        self.sent = []

    def send_email(self, to, subject, key=None):
        if to.startswith("bounce"):
            raise MailError(f"provider rejected {to}")
        self.sent.append((to, subject))


@pytest.fixture
def mailer():
    return RecordingMailer()


import copy
import time

import pytest


@pytest.fixture
def fake_world():
    """A transactional in-memory world (chapter 7.3): the store survives between units of work; a unit of work works on a
    private copy that replaces the store only on commit(). It implements the repository interface of problem p025."""
    from solution import NotFound, Task

    class TaskRepo:
        def __init__(self, data):
            self.data = data

        def add(self, task):
            task.id = self.data["next_id"]
            self.data["next_id"] += 1
            self.data["tasks"][task.id] = copy.copy(task)
            return task

        def get(self, task_id):
            if task_id not in self.data["tasks"]:
                raise NotFound(f"task {task_id} not found")
            return copy.copy(self.data["tasks"][task_id])

        def save(self, task):
            self.data["tasks"][task.id] = copy.copy(task)

        def list_for_project(self, project_id, status=None):
            rows = sorted(self.data["tasks"].values(), key=lambda t: t.id)
            return [copy.copy(t) for t in rows if t.project_id == project_id and (status is None or t.status == status)]

        def open_count_for(self, user_id):
            return sum(1 for t in self.data["tasks"].values() if t.assignee_id == user_id and t.status != "done")

        def add_audit(self, task_id, action, at):
            self.data["audit"].append((task_id, action))

        def audit_for(self, task_id):
            return [a for tid, a in self.data["audit"] if tid == task_id]

    class ProjectRepo:
        def __init__(self, data):
            self.data = data

        def exists(self, project_id):
            return project_id in self.data["projects"]

        def is_member(self, project_id, user_id):
            return (project_id, user_id) in self.data["members"]

    class UserRepo:
        def __init__(self, data):
            self.data = data

        def email_of(self, user_id):
            return self.data["users"][user_id]

    class FakeStore:
        def __init__(self):
            self.data = {"tasks": {}, "audit": [], "next_id": 1,
                         "users": {1: "ana@example.com", 2: "ben@example.com", 3: "cy@example.com", 4: "bounce@example.com"},
                         "projects": {1, 2}, "members": {(1, 1), (1, 2), (1, 4), (2, 3)}}

    class FakeUnitOfWork:
        def __init__(self, store):
            self.store = store
            self.committed = False

        def __enter__(self):
            self.work = copy.deepcopy(self.store.data)             # a private copy = our transaction
            self.tasks, self.projects, self.users = TaskRepo(self.work), ProjectRepo(self.work), UserRepo(self.work)
            return self

        def __exit__(self, exc_type, exc, tb):
            pass                                                    # not committed -> the copy is dropped

        def commit(self):
            self.store.data = self.work
            self.committed = True

    class World:
        def __init__(self):
            self.store = FakeStore()

        def uow(self):
            return FakeUnitOfWork(self.store)

    return World()


