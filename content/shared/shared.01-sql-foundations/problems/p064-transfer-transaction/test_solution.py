import ast
import inspect
import sqlite3

import pytest

import solution
from solution import transfer

SCHEMA = """CREATE TABLE accounts (id INTEGER PRIMARY KEY, owner TEXT, balance INTEGER NOT NULL CHECK (balance >= 0));
INSERT INTO accounts VALUES (1, 'Ada', 100), (2, 'Bo', 50), (3, 'Cy', 0);"""


@pytest.fixture()
def db(tmp_path):
    path = str(tmp_path / "bank.db")
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    con.commit()
    yield path, con
    con.close()


def balances(path):
    other = sqlite3.connect(path)          # a second connection sees only committed data
    try:
        return dict(other.execute("SELECT id, balance FROM accounts").fetchall())
    finally:
        other.close()


def test_success_is_committed(db):
    path, con = db
    assert transfer(con, 1, 2, 30) is None, "transfer returns None."
    assert balances(path) == {1: 70, 2: 80, 3: 0}, "After a successful transfer the change must be COMMITTED (visible to another connection)."
    assert not con.in_transaction, "No transaction may be left open after success."


def test_exact_balance_allowed(db):
    path, con = db
    transfer(con, 2, 3, 50)
    assert balances(path) == {1: 100, 2: 0, 3: 50}, "Moving the whole balance is allowed (balance >= amount)."


def test_insufficient_funds_raises_value_error(db):
    path, con = db
    with pytest.raises(ValueError):
        transfer(con, 1, 2, 500)
    assert balances(path) == {1: 100, 2: 50, 3: 0}, "Nothing may change after a failed transfer."
    assert not con.in_transaction, "Roll back (or never start) the transaction: none may stay open."


@pytest.mark.parametrize("args", [(1, 2, 0), (1, 2, -5), (1, 1, 10)])
def test_bad_amount_or_same_account(db, args):
    path, con = db
    with pytest.raises(ValueError):
        transfer(con, *args)
    assert balances(path) == {1: 100, 2: 50, 3: 0}


def test_missing_source(db):
    path, con = db
    with pytest.raises(KeyError):
        transfer(con, 99, 2, 10)
    assert balances(path) == {1: 100, 2: 50, 3: 0}


def test_missing_target_undoes_the_debit(db):
    path, con = db
    with pytest.raises(KeyError):
        transfer(con, 1, 99, 10)
    assert balances(path) == {1: 100, 2: 50, 3: 0}, \
        "Account 99 does not exist: the 10 taken from Ada must be rolled back. Do the work inside `with con:` and raise inside it."
    assert not con.in_transaction, "The failed transfer left a transaction open."


def test_works_after_a_failure(db):
    path, con = db
    with pytest.raises(ValueError):
        transfer(con, 3, 1, 5)
    transfer(con, 1, 3, 25)
    assert balances(path) == {1: 75, 2: 50, 3: 25}, "The connection must be usable after a failed transfer."


def test_uses_parameters_not_fstrings():
    tree = ast.parse(inspect.getsource(solution))
    assert not any(isinstance(n, ast.JoinedStr) for n in ast.walk(tree)), "Do not build SQL with f-strings; use ? parameters."
