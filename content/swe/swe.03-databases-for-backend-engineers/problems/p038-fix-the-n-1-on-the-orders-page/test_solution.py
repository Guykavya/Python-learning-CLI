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



from sqlalchemy import select, text

from solution import Base, Customer, Order, OrderLine, orders_page


@pytest.fixture
def engine():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with Session(e) as s:
        for i in range(1, 61):
            s.add(Customer(name=f"C{i}", orders=[Order(lines=[OrderLine(sku=f"S{i}-{j}", qty=j + 1, price_paise=100) for j in range(i % 4)])]))
        s.commit()
    return e


def expected(engine):
    with engine.connect() as c:
        orders = c.execute(text("SELECT o.id, c.name FROM orders o JOIN customers c ON c.id = o.customer_id ORDER BY o.id LIMIT 50")).all()
        out = []
        for oid, name in orders:
            lines = c.execute(text("SELECT sku, qty FROM order_lines WHERE order_id = :o ORDER BY id"), {"o": oid}).all()
            out.append({"id": oid, "customer": name, "lines": [{"sku": s, "qty": q} for s, q in lines]})
        return out


def test_result_is_unchanged(engine):
    with Session(engine) as s:
        assert orders_page(s) == expected(engine), "The page must contain exactly the same data as before (50 orders, lines sorted by id)."


def test_at_most_three_queries(engine):
    with Session(engine) as s:
        log = QueryLog(engine)
        page = orders_page(s)
        assert len(page) == 50
        first_repeat = next((st for st in log.statements if log.statements.count(st) > 1), None)
        assert log.count <= 3, (f"{log.count} SQL statements for 50 orders (limit 3). The statement that repeated: {first_repeat!r}. "
                                "Load customer and lines up front with selectinload.")


def test_the_number_of_queries_does_not_grow_with_the_page(engine):
    with Session(engine) as s:
        log = QueryLog(engine)
        orders_page(s)
        small = log.count
    with Session(engine) as s:
        log = QueryLog(engine)
        s.execute(text("DELETE FROM order_lines WHERE order_id > 5"))
        s.execute(text("DELETE FROM orders WHERE id > 5"))
        log.clear()
        orders_page(s)
        assert log.count <= small, "Fewer orders must not need more queries."
