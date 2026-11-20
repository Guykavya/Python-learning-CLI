import pytest
from sqlalchemy import create_engine, text

from solution import count_queries


@pytest.fixture
def engine():
    e = create_engine("sqlite://")
    with e.begin() as c:
        c.execute(text("CREATE TABLE t (x INTEGER)"))
    return e


def run(engine, sql="SELECT 1"):
    with engine.connect() as c:
        c.execute(text(sql))


def test_counts_and_records_statements(engine):
    with count_queries(engine) as q:
        run(engine, "SELECT 1")
        run(engine, "SELECT 2")
    assert q.count == 2, f"Two statements ran, the counter says {q.count}."
    assert q.statements == ["SELECT 1", "SELECT 2"], f"Record the SQL text in order, got {q.statements}."


def test_nothing_before_or_after(engine):
    run(engine)
    with count_queries(engine) as q:
        run(engine)
    run(engine)
    run(engine)
    assert q.count == 1, "Only statements inside the block count; the listener must be removed at the end."


def test_listener_is_removed_also_after_an_exception(engine):
    before = len(engine.dispatch.before_cursor_execute)
    with pytest.raises(RuntimeError):
        with count_queries(engine) as q:
            run(engine)
            raise RuntimeError("boom")
    assert q.count == 1
    assert len(engine.dispatch.before_cursor_execute) == before, "The listener must be removed even when the block raises."
    run(engine)
    assert q.count == 1


def test_no_listener_left_after_a_normal_exit(engine):
    before = len(engine.dispatch.before_cursor_execute)
    with count_queries(engine):
        pass
    assert len(engine.dispatch.before_cursor_execute) == before


def test_nested_counters(engine):
    with count_queries(engine) as outer:
        run(engine)
        with count_queries(engine) as inner:
            run(engine)
            run(engine)
        run(engine)
    assert (outer.count, inner.count) == (4, 2), "The outer counter also sees the inner block; the inner sees only its own."


def test_two_counters_are_independent(engine):
    with count_queries(engine) as a:
        run(engine)
    with count_queries(engine) as b:
        run(engine)
        run(engine)
    assert (a.count, b.count) == (1, 2)


def test_empty_block(engine):
    with count_queries(engine) as q:
        pass
    assert q.count == 0 and q.statements == []
