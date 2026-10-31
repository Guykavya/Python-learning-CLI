import pytest

from target import all_users, create_user, delete_user


@pytest.fixture
def make_user():
    # TODO: return a function make(name, admin=False) that creates users,
    # and delete every user it created after the test.
    pass
