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



from sqlalchemy.exc import InvalidRequestError

from solution import Base, Customer, Order, OrderLine, naive_report, report


@pytest.fixture
def engine():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with Session(e) as s:
        asha = Customer(name="Asha")
        ravi = Customer(name="Ravi")
        s.add_all([asha, ravi])
        s.flush()
        s.add_all([Order(customer_id=asha.id, lines=[OrderLine(sku="A"), OrderLine(sku="B")]),
                   Order(customer_id=asha.id), Order(customer_id=ravi.id, lines=[OrderLine(sku="C")])])
        s.commit()
    return e


def test_report_works(engine):
    with Session(engine) as s:
        assert report(s) == [(1, "Asha", 2), (2, "Asha", 0), (3, "Ravi", 1)]


def test_report_uses_at_most_two_statements(engine):
    with Session(engine) as s:
        log = QueryLog(engine)
        report(s)
        assert log.count <= 2, f"{log.count} statements: load the customer with joinedload and the lines with selectinload."


def test_the_naive_version_is_loud(engine):
    with Session(engine) as s:
        with pytest.raises(InvalidRequestError):
            naive_report(s)


def test_models_still_forbid_lazy_loading(engine):
    for rel in (Customer.orders, Order.customer, Order.lines, OrderLine.order):
        assert rel.property.lazy == "raise", f"{rel} must keep lazy='raise'."
    with Session(engine) as s:
        order = s.get(Order, 1)
        with pytest.raises(InvalidRequestError):
            order.lines


def test_report_with_many_orders_still_two_statements(engine):
    with Session(engine) as s:
        for i in range(40):
            c = Customer(name=f"X{i}")
            s.add(c)
            s.flush()
            s.add(Order(customer_id=c.id, lines=[OrderLine(sku="S")]))
        s.commit()
    with Session(engine) as s:
        log = QueryLog(engine)
        assert len(report(s)) == 43
        assert log.count <= 2
