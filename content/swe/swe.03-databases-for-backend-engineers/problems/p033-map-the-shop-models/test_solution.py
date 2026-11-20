import pytest
from sqlalchemy import create_engine, func, inspect, select
from sqlalchemy.orm import Session

from solution import Base, Customer, Order, OrderLine


@pytest.fixture
def engine():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    return e


def count(session, model):
    return session.scalar(select(func.count()).select_from(model))


def test_tables_and_columns(engine):
    insp = inspect(engine)
    assert set(insp.get_table_names()) == {"customers", "orders", "order_lines"}
    assert {c["name"] for c in insp.get_columns("orders")} == {"id", "customer_id", "total_paise"}
    assert {c["name"] for c in insp.get_columns("order_lines")} == {"id", "order_id", "sku", "qty", "price_paise"}
    fks = {(t, tuple(f["constrained_columns"]), f["referred_table"]) for t in ("orders", "order_lines") for f in insp.get_foreign_keys(t)}
    assert fks == {("orders", ("customer_id",), "customers"), ("order_lines", ("order_id",), "orders")}


def test_one_add_saves_the_whole_graph(engine):
    with Session(engine) as s:
        c = Customer(name="Asha", orders=[Order(lines=[OrderLine(sku="TEA", qty=2, price_paise=25000),
                                                       OrderLine(sku="COF", qty=1, price_paise=30000)])])
        s.add(c)
        s.commit()
        assert (count(s, Customer), count(s, Order), count(s, OrderLine)) == (1, 1, 2)
        assert c.orders[0].customer is c and c.orders[0].lines[0].order is c.orders[0], "back_populates keeps both sides in step."
        assert c.orders[0].total_paise == 0, "total_paise defaults to 0."


def test_deleting_an_order_deletes_its_lines(engine):
    with Session(engine) as s:
        o = Order(lines=[OrderLine(sku="A", qty=1, price_paise=1), OrderLine(sku="B", qty=1, price_paise=1)])
        s.add(Customer(name="X", orders=[o]))
        s.commit()
        s.delete(o)
        s.commit()
        assert count(s, Order) == 0 and count(s, OrderLine) == 0, "cascade='all' deletes the lines with the order."
        assert count(s, Customer) == 1, "The customer stays."


def test_removing_a_line_from_the_list_deletes_it(engine):
    with Session(engine) as s:
        o = Order(lines=[OrderLine(sku="A", qty=1, price_paise=1), OrderLine(sku="B", qty=1, price_paise=1)])
        s.add(Customer(name="X", orders=[o]))
        s.commit()
        o.lines.remove(o.lines[0])
        s.commit()
        assert count(s, OrderLine) == 1, "delete-orphan: a line removed from order.lines is deleted."


def test_customer_orders_are_not_deleted_by_cascade_on_removal(engine):
    with Session(engine) as s:
        c = Customer(name="X", orders=[Order(), Order()])
        s.add(c)
        s.commit()
        assert [o.customer_id for o in c.orders] == [c.id, c.id]
        assert Customer.orders.property.cascade.delete_orphan is False, "Only Order.lines has delete-orphan."
