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



from solution import Base, Customer, Order, top_customers


@pytest.fixture
def session():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with Session(e) as s:
        s.add_all([
            Customer(name="Asha", orders=[Order(total_paise=25000), Order(total_paise=50000)]),
            Customer(name="Ravi", orders=[Order(total_paise=30000), Order(total_paise=30000), Order(total_paise=30000)]),
            Customer(name="Meena", orders=[Order(total_paise=75000)]),
            Customer(name="Zoya", orders=[Order(total_paise=90000)]),
            Customer(name="Idle"),
            Customer(name="Asha", orders=[Order(total_paise=1)]),       # a second customer with the same name
        ])
        s.commit()
        yield s


def test_the_example_rows(session):
    got = top_customers(session, 2)
    assert got == [("Ravi", 3, 90000), ("Zoya", 1, 90000)], f"Total desc, ties by name (Ravi before Zoya). Got {got}."


def test_ties_are_broken_by_name_and_n_limits(session):
    got = top_customers(session, 4)
    assert got == [("Ravi", 3, 90000), ("Zoya", 1, 90000), ("Asha", 2, 75000), ("Meena", 1, 75000)], (
        f"Total descending; equal totals by name ascending (90000: Ravi, Zoya; 75000: Asha, Meena). Got {got}.")


def test_customers_without_orders_are_not_listed(session):
    names = [r[0] for r in top_customers(session, 100)]
    assert "Idle" not in names


def test_fewer_than_n_and_zero(session):
    assert len(top_customers(session, 100)) == 5
    assert top_customers(session, 0) == []


def test_two_customers_with_the_same_name_stay_separate(session):
    got = top_customers(session, 100)
    asha = [r for r in got if r[0] == "Asha"]
    assert sorted(asha) == [("Asha", 1, 1), ("Asha", 2, 75000)], "Group by the customer id, not only by the name."


def test_one_query_and_the_database_does_the_work(session):
    log = QueryLog(session.get_bind())
    top_customers(session, 3)
    assert log.count == 1, f"Use one SELECT with JOIN, GROUP BY, ORDER BY and LIMIT; {log.count} statements ran."
    assert "GROUP BY" in log.statements[0].upper() and "LIMIT" in log.statements[0].upper()
