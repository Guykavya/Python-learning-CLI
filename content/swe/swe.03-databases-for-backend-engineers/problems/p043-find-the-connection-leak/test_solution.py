import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import TimeoutError as PoolTimeout
from sqlalchemy.pool import QueuePool

from solution import lookup


@pytest.fixture
def engine(tmp_path):
    e = create_engine(f"sqlite:///{tmp_path / 'u.db'}", poolclass=QueuePool, pool_size=2, max_overflow=0, pool_timeout=1)
    with e.begin() as c:
        c.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"))
        c.execute(text("INSERT INTO users VALUES (1, 'Asha'), (2, 'Ravi')"))
    return e


def test_success_path(engine):
    assert lookup(engine, 1) == "Asha"
    assert engine.pool.checkedout() == 0


def test_error_path_returns_the_connection(engine):
    with pytest.raises(KeyError):
        lookup(engine, 99)
    assert engine.pool.checkedout() == 0, "The connection must go back to the pool when the user is missing."


def test_ten_calls_some_failing(engine):
    for i in range(10):
        user = 1 if i % 2 == 0 else 100 + i
        try:
            if user == 1:
                assert lookup(engine, user) == "Asha"
            else:
                with pytest.raises(KeyError):
                    lookup(engine, user)
        except PoolTimeout:
            pytest.fail(f"Call {i}: the pool is exhausted (pool_size=2, no overflow): a connection leaked on the error path.")
    assert engine.pool.checkedout() == 0, f"{engine.pool.checkedout()} connection(s) were never returned to the pool."


def test_keyerror_carries_the_id(engine):
    with pytest.raises(KeyError) as e:
        lookup(engine, 42)
    assert e.value.args == (42,)
