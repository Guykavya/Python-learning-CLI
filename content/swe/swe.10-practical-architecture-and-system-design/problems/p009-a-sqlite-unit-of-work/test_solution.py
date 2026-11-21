import sqlite3

import pytest

from solution import SqliteUnitOfWork, Task


def new(title="x", **kw):
    base = dict(id=None, project_id=1, title=title, status="todo", assignee_id=None, created_at="2026-01-01T00:00:00")
    return Task(**{**base, **kw})


def titles(path):
    with SqliteUnitOfWork(path) as check:
        return [t.title for t in check.tasks.list_for_project(1)]


def test_commit_saves(db_path):
    with SqliteUnitOfWork(db_path) as uow:
        uow.tasks.add(new("saved"))
        uow.commit()
    assert titles(db_path) == ["saved"], "After commit() a NEW unit of work (a new connection) must see the data."


def test_leaving_without_commit_rolls_back(db_path):
    with SqliteUnitOfWork(db_path) as uow:
        uow.tasks.add(new("ghost"))
    assert titles(db_path) == [], "A forgotten commit() must leave no trace: __exit__ always rolls back."


def test_an_exception_rolls_back_and_propagates(db_path):
    with pytest.raises(RuntimeError, match="boom"):
        with SqliteUnitOfWork(db_path) as uow:
            uow.tasks.add(new("doomed"))
            raise RuntimeError("boom")
    assert titles(db_path) == [], "A failure inside the block must undo the work."


def test_an_exception_after_commit_keeps_the_committed_data(db_path):
    with pytest.raises(RuntimeError):
        with SqliteUnitOfWork(db_path) as uow:
            uow.tasks.add(new("kept"))
            uow.commit()
            raise RuntimeError("too late to matter")
    assert titles(db_path) == ["kept"], "What was committed stays; the rollback in __exit__ has nothing left to undo."


def test_all_repositories_share_one_transaction(db_path):
    with SqliteUnitOfWork(db_path) as uow:
        t = uow.tasks.add(new("with audit"))
        uow.tasks.add_audit(t.id, "created", "now")
        assert uow.tasks.conn is uow.projects.conn is uow.users.conn is uow.conn, "All repositories must use the unit of work's own connection."
        uow.commit()
    with SqliteUnitOfWork(db_path) as check:
        assert check.tasks.audit_for(1) == ["created"]


def test_task_and_audit_line_succeed_or_fail_together(db_path):
    with pytest.raises(RuntimeError):
        with SqliteUnitOfWork(db_path) as uow:
            t = uow.tasks.add(new("half"))
            uow.tasks.add_audit(t.id, "created", "now")
            raise RuntimeError("crash before commit")
    with SqliteUnitOfWork(db_path) as check:
        assert check.tasks.list_for_project(1) == [] and check.tasks.audit_for(1) == [], "Neither the task nor its audit line may survive: that is all-or-nothing."


def test_the_connection_is_closed_after_the_block(db_path):
    with SqliteUnitOfWork(db_path) as uow:
        conn = uow.conn
        conn.execute("SELECT 1")
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")


def test_enter_returns_the_unit_of_work_and_each_use_opens_a_new_connection(db_path):
    uow = SqliteUnitOfWork(db_path)
    with uow as first:
        assert first is uow
        c1 = uow.conn
    with uow:
        c2 = uow.conn
    assert c1 is not c2, "Every `with` block opens its own connection (one per use case)."


def test_failed_use_case_does_not_disturb_a_later_one(db_path):
    with pytest.raises(RuntimeError):
        with SqliteUnitOfWork(db_path) as uow:
            uow.tasks.add(new("orphan"))
            raise RuntimeError("fails after the insert")
    with SqliteUnitOfWork(db_path) as uow:
        uow.tasks.add(new("next"))
        uow.commit()
    assert titles(db_path) == ["next"], "The shared-connection bug of chapter 3.1: the orphan must NOT be committed by the next request."


def test_commit_is_visible_to_reads_in_the_same_block(db_path):
    with SqliteUnitOfWork(db_path) as uow:
        uow.tasks.add(new("a"))
        assert [t.title for t in uow.tasks.list_for_project(1)] == ["a"], "Inside the transaction the work is visible to its own reads, even before commit."
