import pytest

from solution import NotFound, SqliteTaskRepo, Task


@pytest.fixture
def repo(conn):
    return SqliteTaskRepo(conn)


def new(**kw):
    base = dict(id=None, project_id=1, title="t", status="todo", assignee_id=None, created_at="2026-01-01T00:00:00")
    return Task(**{**base, **kw})


def test_add_sets_the_id_and_get_returns_equal_data(repo):
    t = repo.add(new(title="hello", assignee_id=1))
    assert t.id == 1, "add must set the id on the task (the database made it)."
    again = repo.get(t.id)
    assert again == t, "get must return a Task with the same data."
    assert isinstance(again, Task), "Return Task objects, never sqlite3.Row."


def test_ids_increase(repo):
    assert [repo.add(new()).id for _ in range(3)] == [1, 2, 3]


def test_get_unknown_raises_not_found(repo):
    with pytest.raises(NotFound, match="99"):
        repo.get(99)


def test_get_returns_a_new_object_each_time(repo):
    t = repo.add(new(title="old"))
    first = repo.get(t.id)
    first.title = "changed but not saved"
    assert repo.get(t.id).title == "old", "Unsaved changes must not leak: every get builds a new Task from the row."


def test_save_persists_the_changes(repo):
    t = repo.add(new(assignee_id=1))
    t.title, t.status, t.assignee_id, t.completed_at = "renamed", "done", 2, "2026-02-02T00:00:00"
    repo.save(t)
    got = repo.get(t.id)
    assert (got.title, got.status, got.assignee_id, got.completed_at) == ("renamed", "done", 2, "2026-02-02T00:00:00")


def test_save_can_clear_values(repo):
    t = repo.add(new(assignee_id=1, status="done", completed_at="x"))
    t.assignee_id, t.completed_at, t.status = None, None, "todo"
    repo.save(t)
    got = repo.get(t.id)
    assert (got.assignee_id, got.completed_at, got.status) == (None, None, "todo"), "None must be stored as NULL, not as the text 'None'."


def test_open_count_ignores_done_other_people_and_nobody(repo):
    repo.add(new(assignee_id=1))
    repo.add(new(assignee_id=1, status="doing"))
    repo.add(new(assignee_id=1, status="done"))
    repo.add(new(assignee_id=2))
    repo.add(new(assignee_id=None))
    assert repo.open_count_for(1) == 2, "Only the non-done tasks of that user count."
    assert repo.open_count_for(2) == 1
    assert repo.open_count_for(3) == 0


def test_list_is_ordered_by_id_and_filtered(repo):
    a = repo.add(new(title="a", status="doing"))
    b = repo.add(new(title="b"))
    repo.add(new(title="elsewhere", project_id=2))
    assert [t.id for t in repo.list_for_project(1)] == [a.id, b.id], "Only that project's tasks, ordered by id."
    assert [t.id for t in repo.list_for_project(1, "doing")] == [a.id], "An optional status filter."
    assert repo.list_for_project(1, "done") == []
    assert [t.title for t in repo.list_for_project(2)] == ["elsewhere"]


def test_add_and_save_do_not_commit(conn, repo):
    t = repo.add(new(title="uncommitted"))
    t.title = "still uncommitted"
    repo.save(t)
    conn.rollback()
    assert conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0, "The repository must not call commit(): the caller owns the transaction."


def test_the_repository_returns_no_rows(repo):
    repo.add(new())
    for task in repo.list_for_project(1):
        assert type(task) is Task
