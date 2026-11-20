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



from sqlalchemy import ForeignKey, String, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

from solution import assert_max_queries


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship()


def page_bad(session):
    return [(o.id, o.customer.name) for o in session.scalars(select(Order).order_by(Order.id))]


def page_good(session):
    return [(o.id, o.customer.name) for o in session.scalars(select(Order).order_by(Order.id).options(selectinload(Order.customer)))]


@pytest.fixture
def engine():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with Session(e) as s:
        for i in range(6):
            s.add(Order(customer=Customer(name=f"C{i}")))
        s.commit()
    return e


def test_a_good_function_passes(engine):
    with Session(engine) as s:
        with assert_max_queries(engine, 2):
            assert len(page_good(s)) == 6


def test_a_bad_function_fails_with_the_statements_listed(engine):
    with Session(engine) as s:
        with pytest.raises(AssertionError) as e:
            with assert_max_queries(engine, 2):
                page_bad(s)
    msg = str(e.value)
    assert "2" in msg and "7" in msg, f"Say the limit (2) and the real count (7). Got: {msg!r}"
    assert msg.count("FROM customers") == 6, "List every statement: the repeated one must be visible 6 times."
    assert "1." in msg and "7." in msg, "Number the statements."


def test_exactly_n_is_allowed_and_zero_works(engine):
    with Session(engine) as s:
        with assert_max_queries(engine, 7):
            page_bad(s)
    with assert_max_queries(engine, 0):
        pass
    with pytest.raises(AssertionError):
        with assert_max_queries(engine, 0):
            with engine.connect() as c:
                c.execute(text("SELECT 1"))


def test_the_blocks_own_exception_is_not_hidden(engine):
    with pytest.raises(ZeroDivisionError):
        with assert_max_queries(engine, 0):
            with engine.connect() as c:
                c.execute(text("SELECT 1"))
            1 / 0


def test_the_listener_is_always_removed(engine):
    before = len(engine.dispatch.before_cursor_execute)
    with pytest.raises(AssertionError):
        with assert_max_queries(engine, 0):
            with engine.connect() as c:
                c.execute(text("SELECT 1"))
    with pytest.raises(RuntimeError):
        with assert_max_queries(engine, 5):
            raise RuntimeError("x")
    with assert_max_queries(engine, 5):
        pass
    assert len(engine.dispatch.before_cursor_execute) == before


def test_statements_before_the_block_do_not_count(engine):
    with engine.connect() as c:
        c.execute(text("SELECT 1"))
        c.execute(text("SELECT 2"))
    with assert_max_queries(engine, 1):
        with engine.connect() as c:
            c.execute(text("SELECT 3"))
