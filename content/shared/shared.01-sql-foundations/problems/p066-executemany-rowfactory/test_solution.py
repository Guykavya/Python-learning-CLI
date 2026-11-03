import sqlite3

import pytest

from solution import add_books, books_as_dicts, average_by_category

SCHEMA = """CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, category TEXT, price REAL NOT NULL CHECK (price > 0));"""


@pytest.fixture()
def con():
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA)
    return c


def count(c):
    return c.execute("SELECT COUNT(*) FROM books").fetchone()[0]


def test_add_books_returns_count(con):
    assert add_books(con, [("A", "Tech", 10), ("B", "Tech", 20)]) == 2, "Return the number of rows inserted."
    assert count(con) == 2
    assert add_books(con, []) == 0, "An empty list inserts nothing and returns 0."


def test_add_books_commits(tmp_path):
    path = str(tmp_path / "s.db")
    c = sqlite3.connect(path)
    c.executescript(SCHEMA)
    add_books(c, [("A", "Tech", 10)])
    other = sqlite3.connect(path)
    assert other.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 1, "The insert must be committed (with con: ...)."


def test_add_books_all_or_nothing(con):
    add_books(con, [("A", "Tech", 10)])
    with pytest.raises(sqlite3.IntegrityError):
        add_books(con, [("C", "Tech", 5), ("D", "Tech", 0), ("E", "Tech", 7)])
    assert count(con) == 1, "One invalid row (price 0) must undo the whole batch: C must not stay. Use `with con:` around executemany."
    assert not con.in_transaction, "No transaction may stay open after the error."


def test_books_as_dicts(con):
    add_books(con, [("B", "Tech", 20), ("A", "Tech", 10), ("Z", "Maps", 5.5)])
    got = books_as_dicts(con, "Tech")
    assert got == [{"title": "A", "price": 10.0}, {"title": "B", "price": 20.0}], "Return plain dicts with keys title and price, ordered by title."
    assert all(type(d) is dict for d in got), "Convert each sqlite3.Row with dict(row)."
    assert books_as_dicts(con, "None here") == []


def test_row_factory_restored(con):
    add_books(con, [("A", "Tech", 10)])
    books_as_dicts(con, "Tech")
    assert con.row_factory is None, "Restore the original row_factory before returning."
    con.row_factory = sqlite3.Row
    books_as_dicts(con, "Tech")
    assert con.row_factory is sqlite3.Row, "Restore whatever the previous row_factory was, not always None."


def test_row_factory_restored_on_error():
    c = sqlite3.connect(":memory:")          # no books table: the query fails
    with pytest.raises(sqlite3.Error):
        books_as_dicts(c, "Tech")
    assert c.row_factory is None, "Use try/finally so the row_factory is restored even when the query fails."


def test_average_and_closing(tmp_path, monkeypatch):
    path = str(tmp_path / "avg.db")
    c = sqlite3.connect(path)
    c.executescript(SCHEMA)
    add_books(c, [("A", "Tech", 10), ("B", "Tech", 15), ("C", "Tech", 20.5), ("D", "Maps", 7)])
    c.close()
    made = []
    real = sqlite3.connect

    def spy(*a, **k):
        con = real(*a, **k)
        made.append(con)
        return con

    monkeypatch.setattr(sqlite3, "connect", spy)
    assert average_by_category(path) == {"Maps": 7.0, "Tech": 15.17}, "Average per category rounded to 2 decimals."
    assert len(made) == 1, "Open exactly one connection."
    with pytest.raises(sqlite3.ProgrammingError):
        made[0].execute("SELECT 1")
    # closed also on error: break the table name
    made.clear()
    other = str(tmp_path / "empty.db")
    real(other).close()
    with pytest.raises(sqlite3.Error):
        average_by_category(other)
    assert made, "A connection should have been opened."
    with pytest.raises(sqlite3.ProgrammingError):
        made[0].execute("SELECT 1")
