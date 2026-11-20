import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session


class QueryLog:
    def __init__(self, engine):
        self.statements = []
        event.listen(engine, "before_cursor_execute", self._record)

    def _record(self, conn, cursor, statement, parameters, context, executemany):
        self.statements.append(statement)

    @property
    def count(self):
        return len(self.statements)

    def clear(self):
        self.statements.clear()



from sqlalchemy import select

from solution import Base, User, add_users


@pytest.fixture
def session():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with Session(e) as s:
        yield s


def emails(session):
    return sorted(session.scalars(select(User.email)))


def test_all_new(session):
    assert add_users(session, ["a@x.com", "b@x.com"]) == (2, [])
    assert emails(session) == ["a@x.com", "b@x.com"]


def test_duplicates_inside_the_list_are_skipped(session):
    assert add_users(session, ["a@x.com", "b@x.com", "a@x.com", "c@x.com", "b@x.com"]) == (3, ["a@x.com", "b@x.com"]), (
        "The second a@x.com and the second b@x.com are skipped, in order; the others are kept.")
    assert emails(session) == ["a@x.com", "b@x.com", "c@x.com"]


def test_addresses_already_in_the_database_are_skipped(session):
    session.add(User(email="old@x.com"))
    session.commit()
    assert add_users(session, ["new@x.com", "old@x.com", "new2@x.com"]) == (2, ["old@x.com"])
    assert emails(session) == ["new2@x.com", "new@x.com", "old@x.com"]


def test_the_session_is_usable_afterwards(session):
    add_users(session, ["a@x.com", "a@x.com"])
    session.add(User(email="z@x.com"))
    session.commit()
    assert emails(session) == ["a@x.com", "z@x.com"], "No PendingRollbackError: the failure must be confined to a savepoint."


def test_good_users_before_the_failure_survive(session):
    add_users(session, ["a@x.com", "b@x.com", "c@x.com", "a@x.com"])
    assert emails(session) == ["a@x.com", "b@x.com", "c@x.com"], "A failed user must not undo the earlier ones."


def test_committed(session, tmp_path):
    e = create_engine(f"sqlite:///{tmp_path / 'u.db'}")
    Base.metadata.create_all(e)
    with Session(e) as s:
        add_users(s, ["a@x.com", "a@x.com", "b@x.com"])
    with Session(e) as s2:
        assert emails(s2) == ["a@x.com", "b@x.com"], "add_users must commit."


def test_empty_list(session):
    assert add_users(session, []) == (0, [])
