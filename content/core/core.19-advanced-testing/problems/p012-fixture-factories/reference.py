import pytest

from target import all_users, create_user, delete_user


@pytest.fixture
def make_user():
    created = []

    def make(name, admin=False):
        user = create_user(name, admin=admin)
        created.append(name)
        return user

    yield make
    for name in created:
        if name in all_users():
            delete_user(name)
