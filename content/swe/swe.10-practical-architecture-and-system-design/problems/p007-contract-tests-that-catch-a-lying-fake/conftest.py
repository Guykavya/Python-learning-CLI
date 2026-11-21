"""Course helpers for this problem (copied from the chapter). The tests receive them as fixtures; your solution never imports this file."""
import sqlite3

import pytest


class SqliteProjectRepo:
    """The real repository: members are people's handles, compared without regard to case."""

    def __init__(self, conn):
        self.conn = conn
        conn.execute("CREATE TABLE IF NOT EXISTS project_members ("
                     "project_id INTEGER NOT NULL, handle TEXT NOT NULL COLLATE NOCASE, PRIMARY KEY (project_id, handle))")

    def add_member(self, project_id, handle):
        self.conn.execute("INSERT OR IGNORE INTO project_members (project_id, handle) VALUES (?, ?)", (project_id, handle.lower()))

    def is_member(self, project_id, handle):
        return self.conn.execute("SELECT 1 FROM project_members WHERE project_id = ? AND handle = ?",
                                 (project_id, handle)).fetchone() is not None

    def members(self, project_id):
        return sorted(r[0] for r in self.conn.execute("SELECT handle FROM project_members WHERE project_id = ?", (project_id,)))


class HonestFake:
    """A careful in-memory repository: same behaviour as the real one."""

    def __init__(self):
        self.rows = set()

    def add_member(self, project_id, handle):
        self.rows.add((project_id, handle.lower()))

    def is_member(self, project_id, handle):
        return (project_id, handle.lower()) in self.rows

    def members(self, project_id):
        return sorted(h for p, h in self.rows if p == project_id)


class DuplicatingFake:
    """LIE 1: adding the same member twice keeps two entries."""

    def __init__(self):
        self.rows = []

    def add_member(self, project_id, handle):
        self.rows.append((project_id, handle.lower()))

    def is_member(self, project_id, handle):
        return (project_id, handle.lower()) in self.rows

    def members(self, project_id):
        return sorted(h for p, h in self.rows if p == project_id)


class CaseSensitiveFake:
    """LIE 2: handles are compared and stored exactly as given."""

    def __init__(self):
        self.rows = set()

    def add_member(self, project_id, handle):
        self.rows.add((project_id, handle))

    def is_member(self, project_id, handle):
        return (project_id, handle) in self.rows

    def members(self, project_id):
        return sorted(h for p, h in self.rows if p == project_id)


class ProjectBlindFake:
    """LIE 3: membership ignores which project it is about."""

    def __init__(self):
        self.handles = set()

    def add_member(self, project_id, handle):
        self.handles.add(handle.lower())

    def is_member(self, project_id, handle):
        return handle.lower() in self.handles

    def members(self, project_id):
        return sorted(self.handles)


@pytest.fixture
def honest_repos():
    """Factories that build a FRESH honest repository each time they are called."""
    def sqlite_factory():
        connection = sqlite3.connect(":memory:")
        return SqliteProjectRepo(connection)

    return {"sqlite": sqlite_factory, "honest fake": HonestFake}


@pytest.fixture
def lying_repos():
    return {"duplicating fake": DuplicatingFake, "case-sensitive fake": CaseSensitiveFake, "project-blind fake": ProjectBlindFake}


