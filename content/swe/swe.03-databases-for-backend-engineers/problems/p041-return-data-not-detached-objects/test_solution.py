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



import json

from solution import Base, Customer, Order, customer_summary


@pytest.fixture
def engine():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with Session(e) as s:
        s.add(Customer(name="Asha", orders=[Order(total_paise=5000), Order(total_paise=700)]))
        s.add(Customer(name="Ravi"))
        s.commit()
    return e


def test_plain_data_comes_back(engine):
    got = customer_summary(engine, 1)
    assert got == {"id": 1, "name": "Asha", "orders": [{"id": 1, "total_paise": 5000}, {"id": 2, "total_paise": 700}]}, f"Got {got!r}."


def test_it_can_be_used_after_the_session_is_closed(engine):
    got = customer_summary(engine, 1)
    assert json.dumps(got), "The result must be plain data: json.dumps must work."
    assert got["orders"][1]["total_paise"] == 700


def test_a_customer_without_orders(engine):
    assert customer_summary(engine, 2) == {"id": 2, "name": "Ravi", "orders": []}


def test_unknown_customer(engine):
    assert customer_summary(engine, 99) is None


def test_no_orm_objects_in_the_result(engine):
    def check(x):
        assert isinstance(x, (dict, list, str, int, float, type(None))), f"{type(x)} found in the result: only plain data."
        if isinstance(x, dict):
            [check(v) for v in x.values()]
        if isinstance(x, list):
            [check(v) for v in x]

    check(customer_summary(engine, 1))


def test_at_most_two_statements(engine):
    log = QueryLog(engine)
    customer_summary(engine, 1)
    assert log.count <= 2, f"{log.count} statements: load the orders together with the customer."
