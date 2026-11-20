import pytest
from sqlalchemy import create_engine, select

from solution import add_many, by_city, customers, metadata, remove, rename


@pytest.fixture
def engine():
    e = create_engine("sqlite://")
    metadata.create_all(e)
    return e


def names(engine):
    with engine.connect() as conn:
        return sorted(r[0] for r in conn.execute(select(customers.c.name)))


def test_add_many_and_by_city(engine):
    n = add_many(engine, [{"name": "Ravi", "city": "Pune"}, {"name": "Asha", "city": "Pune"}, {"name": "Meena", "city": "Goa"}])
    assert n == 3
    assert by_city(engine, "Pune") == ["Asha", "Ravi"], "Names of that city only, sorted."
    assert by_city(engine, "Goa") == ["Meena"] and by_city(engine, "Nowhere") == []


def test_add_many_commits(engine, tmp_path):
    e = create_engine(f"sqlite:///{tmp_path / 'c.db'}")
    metadata.create_all(e)
    add_many(e, [{"name": "A", "city": "X"}])
    e2 = create_engine(f"sqlite:///{tmp_path / 'c.db'}")
    assert names(e2) == ["A"], "Writes must be committed: use engine.begin()."


def test_empty_list(engine):
    assert add_many(engine, []) == 0
    assert names(engine) == []


def test_add_many_is_all_or_nothing(engine):
    with pytest.raises(Exception):
        add_many(engine, [{"name": "Good", "city": "X"}, {"name": None, "city": "X"}])
    assert names(engine) == [], "A failing row must roll back the whole batch."


def test_rename_and_remove_return_counts(engine):
    add_many(engine, [{"name": "Asha", "city": "Pune"}])
    assert rename(engine, 1, "Asha K.") == 1 and names(engine) == ["Asha K."]
    assert rename(engine, 99, "Nobody") == 0
    assert remove(engine, 99) == 0 and names(engine) == ["Asha K."]
    assert remove(engine, 1) == 1 and names(engine) == []


def test_city_may_be_missing(engine):
    add_many(engine, [{"name": "NoCity"}])
    assert names(engine) == ["NoCity"] and by_city(engine, "Pune") == []
