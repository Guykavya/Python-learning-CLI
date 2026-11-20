import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from solution import Base, Customer, pending

EMPTY = {"new": [], "dirty": [], "deleted": []}


@pytest.fixture
def session():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with Session(e) as s:
        s.add_all([Customer(name="Asha"), Customer(name="Ravi"), Customer(name="Meena")])
        s.commit()
        yield s


def test_a_clean_session(session):
    assert pending(session) == EMPTY


def test_new_objects(session):
    session.add(Customer(name="Zed"))
    session.add(Customer(name="Bo"))
    assert pending(session) == {"new": ["Bo", "Zed"], "dirty": [], "deleted": []}, "Names, sorted."


def test_flush_empties_new(session):
    session.add(Customer(name="Zed"))
    session.flush()
    assert pending(session) == EMPTY, "After the flush the INSERT has run: nothing is pending."


def test_dirty_objects(session):
    asha = session.query(Customer).filter_by(name="Asha").one()
    asha.name = "Asha K."
    assert pending(session) == {"new": [], "dirty": ["Asha K."], "deleted": []}
    session.flush()
    assert pending(session) == EMPTY


def test_deleted_objects(session):
    ravi = session.query(Customer).filter_by(name="Ravi").one()
    session.delete(ravi)
    assert pending(session) == {"new": [], "dirty": [], "deleted": ["Ravi"]}
    session.flush()
    assert pending(session) == EMPTY


def test_all_three_at_once(session):
    meena = session.query(Customer).filter_by(name="Meena").one()
    asha = session.query(Customer).filter_by(name="Asha").one()
    session.add(Customer(name="New"))
    meena.name = "M2"
    session.delete(asha)
    assert pending(session) == {"new": ["New"], "dirty": ["M2"], "deleted": ["Asha"]}
