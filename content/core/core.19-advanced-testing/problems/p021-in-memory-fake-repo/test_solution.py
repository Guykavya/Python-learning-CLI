import pytest

from solution import DuplicateUser, FakeUserRepo, UserNotFound


class DictRepo:
    """The 'real' repository of the checker (dict-backed). Same contract as the fake."""

    def __init__(self):
        self.rows = {}

    def add(self, user_id, name):
        if user_id in self.rows:
            raise DuplicateUser(user_id)
        if not name.strip():
            raise ValueError("blank name")
        self.rows[user_id] = name

    def get(self, user_id):
        try:
            return self.rows[user_id]
        except KeyError:
            raise UserNotFound(user_id) from None

    def delete(self, user_id):
        if user_id not in self.rows:
            raise UserNotFound(user_id)
        del self.rows[user_id]

    def names(self):
        return [self.rows[i] for i in sorted(self.rows)]


@pytest.fixture(params=[DictRepo, FakeUserRepo], ids=["real", "fake"])
def repo(request):
    return request.param()


def test_exception_types():
    assert issubclass(UserNotFound, KeyError), "UserNotFound must inherit from KeyError."
    assert issubclass(DuplicateUser, ValueError), "DuplicateUser must inherit from ValueError."


def test_add_then_get(repo):
    repo.add(1, "Ann")
    assert repo.get(1) == "Ann", "get must return the name that add stored."


def test_get_missing(repo):
    with pytest.raises(UserNotFound):
        repo.get(9)


def test_add_duplicate_keeps_the_first_name(repo):
    repo.add(1, "Ann")
    with pytest.raises(DuplicateUser):
        repo.add(1, "Bo")
    assert repo.get(1) == "Ann", "A failed add must not change the stored name."


@pytest.mark.parametrize("blank", ["", "   "])
def test_blank_name_rejected_and_nothing_stored(repo, blank):
    with pytest.raises(ValueError):
        repo.add(1, blank)
    with pytest.raises(UserNotFound):
        repo.get(1)


def test_delete(repo):
    repo.add(1, "Ann")
    repo.delete(1)
    with pytest.raises(UserNotFound):
        repo.get(1)
    repo.add(1, "Bo")
    assert repo.get(1) == "Bo", "After delete the id can be used again."


def test_delete_missing(repo):
    with pytest.raises(UserNotFound):
        repo.delete(5)


def test_names_ordered_by_id(repo):
    repo.add(3, "Cy")
    repo.add(1, "Ann")
    repo.add(2, "Bo")
    assert repo.names() == ["Ann", "Bo", "Cy"], "names() is ordered by user_id, not by insertion or by name."


def test_names_returns_a_new_list(repo):
    repo.add(1, "Ann")
    repo.names().append("Intruder")
    assert repo.names() == ["Ann"], "names() must return a copy; editing it must not change the repo."


def test_two_fakes_do_not_share_data():
    a, b = FakeUserRepo(), FakeUserRepo()
    a.add(1, "Ann")
    assert b.names() == [], "Create the dict in __init__, not in the class body: repos must not share data."
