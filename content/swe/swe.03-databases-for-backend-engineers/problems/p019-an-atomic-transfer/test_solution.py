import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def plan(db, sql, params=()):
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]



import pytest

from solution import transfer


@pytest.fixture
def db():
    d = connect()
    d.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance_paise INTEGER NOT NULL CHECK (balance_paise >= 0))")
    d.executemany("INSERT INTO accounts VALUES (?, ?)", [(1, 1000), (2, 500)])
    d.commit()
    return d


def balances(db):
    return dict(db.execute("SELECT id, balance_paise FROM accounts"))


def test_success(db):
    transfer(db, 1, 2, 300)
    assert balances(db) == {1: 700, 2: 800}
    assert not db.in_transaction, "The transfer must be committed."


def test_the_whole_balance_can_be_moved(db):
    transfer(db, 1, 2, 1000)
    assert balances(db) == {1: 0, 2: 1500}


def test_insufficient_funds_changes_nothing(db):
    with pytest.raises(ValueError, match="insufficient"):
        transfer(db, 1, 2, 1001)
    assert balances(db) == {1: 1000, 2: 500}


def test_missing_destination_undoes_the_debit(db):
    with pytest.raises(LookupError):
        transfer(db, 1, 99, 100)
    assert balances(db) == {1: 1000, 2: 500}, "The debit of account 1 must be rolled back when the credit fails."
    assert not db.in_transaction


def test_missing_source(db):
    with pytest.raises(LookupError):
        transfer(db, 99, 2, 100)
    assert balances(db) == {1: 1000, 2: 500}


@pytest.mark.parametrize("src,dst,paise", [(1, 2, 0), (1, 2, -5), (1, 1, 100)])
def test_bad_arguments(db, src, dst, paise):
    with pytest.raises(ValueError):
        transfer(db, src, dst, paise)
    assert balances(db) == {1: 1000, 2: 500}


def test_other_connections_never_see_a_half_transfer(db, tmp_path):
    path = str(tmp_path / "bank.db")
    a = connect(path)
    a.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance_paise INTEGER NOT NULL CHECK (balance_paise >= 0))")
    a.executemany("INSERT INTO accounts VALUES (?, ?)", [(1, 1000), (2, 500)])
    a.commit()
    with pytest.raises(LookupError):
        transfer(a, 1, 99, 100)
    b = connect(path)
    assert dict(b.execute("SELECT id, balance_paise FROM accounts")) == {1: 1000, 2: 500}
