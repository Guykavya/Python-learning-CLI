import pytest
from sqlalchemy import create_engine, event, insert

from solution import books, metadata, search_books

DATA = [
    ("Python Basics", "Rao", 30000), ("Advanced Python", "Rao", 60000), ("Databases", "Iyer", 45000),
    ("100% Pure SQL", "Iyer", 20000), ("under_score", "Nair", 10000), ("Cooking", "Nair", 15000),
]


@pytest.fixture
def conn():
    e = create_engine("sqlite://")
    metadata.create_all(e)
    with e.begin() as c:
        c.execute(insert(books), [{"title": t, "author": a, "price_paise": p} for t, a, p in DATA])
    with e.connect() as c:
        yield c


def titles(rows):
    return [r[0] for r in rows]


def test_no_filters_returns_everything_ordered_by_title(conn):
    got = search_books(conn)
    assert titles(got) == sorted(t for t, _, _ in DATA)
    assert got[0] == ("100% Pure SQL", "Iyer", 20000), "Rows are tuples (title, author, price_paise)."


def test_each_filter_alone(conn):
    assert titles(search_books(conn, title="python")) == ["Advanced Python", "Python Basics"], "Case-insensitive 'contains'."
    assert sorted(titles(search_books(conn, max_price=20000))) == ["100% Pure SQL", "Cooking", "under_score"]
    assert titles(search_books(conn, author="Rao")) == ["Advanced Python", "Python Basics"]


def test_filters_combine_with_and(conn):
    assert titles(search_books(conn, title="python", max_price=40000)) == ["Python Basics"]
    assert titles(search_books(conn, author="Iyer", max_price=30000)) == ["100% Pure SQL"]
    assert search_books(conn, title="python", author="Nair") == []


def test_orders(conn):
    assert [r[2] for r in search_books(conn, order="price")] == sorted(p for _, _, p in DATA)
    assert [r[1] for r in search_books(conn, order="author")][:2] == ["Iyer", "Iyer"]
    assert titles(search_books(conn, author="Rao", order="price")) == ["Python Basics", "Advanced Python"]


@pytest.mark.parametrize("bad", ["price; DROP TABLE books", "id", "", "TITLE", None, "1"])
def test_order_must_be_on_the_whitelist(conn, bad):
    with pytest.raises(ValueError):
        search_books(conn, order=bad)
    with pytest.raises(ValueError):
        search_books(conn, title="x", order=bad)


def test_wildcards_in_the_search_text_are_literal(conn):
    assert titles(search_books(conn, title="100%")) == ["100% Pure SQL"], "A '%' typed by the user must match only a real '%'."
    assert titles(search_books(conn, title="%")) == ["100% Pure SQL"]
    assert titles(search_books(conn, title="_")) == ["under_score"], "'_' is not 'any character'."


def test_values_are_bound_parameters(conn):
    seen = []
    event.listen(conn.engine, "before_cursor_execute", lambda c, cur, stmt, params, ctx, many: seen.append((stmt, params)))
    search_books(conn, title="Rao'; --", author="O'Brien", max_price=5)
    stmt, params = seen[-1]
    assert "O'Brien" not in stmt and "Rao" not in stmt, f"Values must be bound parameters, not pasted into the SQL: {stmt}"
