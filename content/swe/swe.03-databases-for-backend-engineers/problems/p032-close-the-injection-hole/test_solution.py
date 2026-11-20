import pytest
from sqlalchemy import create_engine, event, text

from solution import find_user


@pytest.fixture
def conn():
    e = create_engine("sqlite://")
    seen = []
    event.listen(e, "before_cursor_execute", lambda c, cur, stmt, params, ctx, many: seen.append((stmt, params)))
    with e.begin() as c:
        c.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"))
        c.execute(text("INSERT INTO users(name) VALUES ('Asha'), ('O''Brien'), ('Ravi')"))
    with e.connect() as c:
        c.seen = seen
        yield c


def test_normal_lookup(conn):
    assert find_user(conn, "Asha") == [(1, "Asha")]
    assert find_user(conn, "Nobody") == []


def test_a_quote_in_the_name(conn):
    assert find_user(conn, "O'Brien") == [(2, "O'Brien")], "A quote is just a character when the value is bound."


@pytest.mark.parametrize("attack", ["' OR 1=1 --", "x' OR '1'='1", "'; DROP TABLE users; --", "Asha' --"])
def test_attacks_find_nothing(conn, attack):
    assert find_user(conn, attack) == [], f"{attack!r} must be looked up as a name, not run as SQL."
    assert conn.execute(text("SELECT COUNT(*) FROM users")).scalar_one() == 3


def test_the_value_is_bound_not_pasted(conn):
    conn.seen.clear()
    find_user(conn, "O'Brien")
    stmt, params = conn.seen[-1]
    assert "O'Brien" not in stmt and "Brien" not in stmt, f"The name appears in the SQL text: {stmt!r}. Use a placeholder."
    assert "O'Brien" in (params if isinstance(params, (tuple, list)) else tuple(params.values())), "The name must travel as a parameter."


def test_returns_plain_tuples(conn):
    rows = find_user(conn, "Ravi")
    assert isinstance(rows, list) and type(rows[0]) is tuple
