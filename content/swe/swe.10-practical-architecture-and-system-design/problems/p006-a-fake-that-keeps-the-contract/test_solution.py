import pytest

from solution import FakeTaskRepo, NotFound, Task


@pytest.fixture(params=["fake", "sqlite"])
def repo(request, sqlite_repo):
    return FakeTaskRepo() if request.param == "fake" else sqlite_repo


def new(**kw):
    base = dict(id=None, project_id=1, title="t", status="todo", assignee_id=None, created_at="2026-01-01T00:00:00")
    return Task(**{**base, **kw})


def test_add_assigns_an_id_and_get_returns_equal_data(repo):
    t = repo.add(new(title="hello"))
    assert t.id is not None, "add must set the id on the object"
    assert repo.get(t.id) == t


def test_ids_increase(repo):
    assert [repo.add(new()).id for _ in range(3)] == [1, 2, 3], "ids are handed out in increasing order, starting at 1"


def test_get_unknown_raises_not_found(repo):
    with pytest.raises(NotFound, match="12345"):
        repo.get(12345)


def test_changes_are_lost_without_save(repo):
    t = repo.add(new(title="old"))
    again = repo.get(t.id)
    again.title = "changed but not saved"
    assert repo.get(t.id).title == "old", "get must return a NEW object each time (copy out), like a real database"


def test_add_stores_a_copy(repo):
    t = repo.add(new(title="old"))
    t.title = "changed after add, never saved"
    assert repo.get(t.id).title == "old", "add must store a copy: changing the object you passed in must not change the stored task"


def test_save_persists_changes(repo):
    t = repo.add(new())
    t.status, t.completed_at, t.assignee_id = "done", "2026-02-02T00:00:00", 2
    repo.save(t)
    got = repo.get(t.id)
    assert (got.status, got.completed_at, got.assignee_id) == ("done", "2026-02-02T00:00:00", 2)


def test_save_stores_a_copy(repo):
    t = repo.add(new(title="a"))
    t.title = "b"
    repo.save(t)
    t.title = "c, after save"
    assert repo.get(t.id).title == "b", "save must store a copy too"


def test_list_is_ordered_and_filtered(repo):
    a = repo.add(new(title="a", status="doing"))
    b = repo.add(new(title="b"))
    repo.add(new(title="elsewhere", project_id=2))
    assert [t.id for t in repo.list_for_project(1)] == [a.id, b.id], "ordered by id, only that project"
    assert [t.id for t in repo.list_for_project(1, "doing")] == [a.id]
    assert repo.list_for_project(1, "done") == []


def test_list_returns_copies(repo):
    repo.add(new(title="old"))
    repo.list_for_project(1)[0].title = "changed"
    assert repo.list_for_project(1)[0].title == "old", "list_for_project must return copies as well"


def test_open_count_ignores_done_and_other_people(repo):
    repo.add(new(assignee_id=1))
    repo.add(new(assignee_id=1, status="doing"))
    repo.add(new(assignee_id=1, status="done"))
    repo.add(new(assignee_id=2))
    repo.add(new(assignee_id=None))
    assert repo.open_count_for(1) == 2, "only non-done tasks of that user"
    assert repo.open_count_for(3) == 0


def test_a_service_rule_runs_on_the_fake_without_a_database():
    """The payoff: a rule of the service layer, tested in microseconds with no SQL (chapter 6.2)."""
    repo = FakeTaskRepo()
    for i in range(3):
        repo.add(new(title=f"t{i}", assignee_id=1))
    assert repo.open_count_for(1) >= 3, "the fourth task of user 1 would have to be refused by the service"
