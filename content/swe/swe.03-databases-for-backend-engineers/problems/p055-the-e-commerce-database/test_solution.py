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



import sqlite3

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError

from solution import (Customer, Order, OrderLine, OutOfStock, Product, RestoreFailed, backup, fingerprint,
                      make_engine, orders_with_totals, place_order, restore_and_verify, seed)


@pytest.fixture
def engine(tmp_path):
    e = make_engine(str(tmp_path / "shop.db"))
    with Session(e) as s:
        seed(s)
    return e


def stock(engine, sku):
    with Session(engine) as s:
        return s.scalar(select(Product.stock).where(Product.sku == sku))


def test_seed_data(engine):
    with Session(engine) as s:
        assert s.scalars(select(Customer.name).order_by(Customer.id)).all() == ["Asha", "Ravi", "Meena"]
        assert {p.sku: (p.price_paise, p.stock) for p in s.scalars(select(Product))} == {
            "TEA": (25000, 10), "COF": (30000, 5), "MUG": (45000, 3), "BOOK": (15000, 20), "PEN": (500, 100)}


# ---- constraints --------------------------------------------------------------------------------------------

@pytest.mark.parametrize("sql", [
    "INSERT INTO products(sku, name, price_paise, stock, version) VALUES ('NEG', 'x', -1, 1, 1)",
    "INSERT INTO products(sku, name, price_paise, stock, version) VALUES ('NEG', 'x', 1, -1, 1)",
    "INSERT INTO products(sku, name, price_paise, stock, version) VALUES ('TEA', 'dup', 1, 1, 1)",
    "INSERT INTO customers(email, name) VALUES ('asha@x.com', 'dup')",
    "INSERT INTO orders(customer_id, total_paise) VALUES (999, 0)",
    "INSERT INTO order_lines(order_id, product_id, qty, unit_price_paise) VALUES (1, 1, 0, 5)",
    "INSERT INTO order_lines(order_id, product_id, qty, unit_price_paise) VALUES (1, 1, 1, -5)",
])
def test_the_database_refuses_bad_rows(engine, sql):
    with Session(engine) as s:
        s.execute(text("INSERT INTO orders(customer_id, total_paise) VALUES (1, 0)")) if "order_lines" in sql else None
        with pytest.raises(IntegrityError):
            s.execute(text(sql))


# ---- orders -------------------------------------------------------------------------------------------------

def test_place_order_stores_prices_and_total(engine):
    with Session(engine) as s:
        oid = place_order(s, 1, [("TEA", 2), ("MUG", 1)])
        order = s.get(Order, oid)
        assert order.total_paise == 95000 and order.customer_id == 1
        assert sorted((l.qty, l.unit_price_paise) for l in order.lines) == [(1, 45000), (2, 25000)]
    assert stock(engine, "TEA") == 8 and stock(engine, "MUG") == 2


def test_old_orders_keep_their_price(engine):
    with Session(engine) as s:
        oid = place_order(s, 1, [("TEA", 1)])
        s.execute(text("UPDATE products SET price_paise = 99999 WHERE sku = 'TEA'"))
        s.commit()
    with Session(engine) as s:
        assert s.get(Order, oid).lines[0].unit_price_paise == 25000, "A line stores the price at the time of the order."


def test_not_enough_stock_is_refused(engine):
    with Session(engine) as s:
        with pytest.raises(OutOfStock):
            place_order(s, 1, [("MUG", 4)])
        assert issubclass(OutOfStock, ValueError)
    assert stock(engine, "MUG") == 3


def test_selling_the_last_unit_works_and_then_refuses(engine):
    with Session(engine) as s:
        place_order(s, 1, [("MUG", 3)])
        with pytest.raises(OutOfStock):
            place_order(s, 2, [("MUG", 1)])
    assert stock(engine, "MUG") == 0


def test_an_order_is_all_or_nothing_and_the_session_survives(engine):
    with Session(engine) as s:
        with pytest.raises(OutOfStock):
            place_order(s, 1, [("TEA", 3), ("COF", 1), ("MUG", 99)])
        assert s.scalar(select(func.count()).select_from(Order)) == 0, "No order may stay."
        assert s.scalar(select(func.count()).select_from(OrderLine)) == 0
        oid = place_order(s, 1, [("PEN", 5)])
        assert oid == 1 or oid > 0, "The session must still work after the failure."
    assert stock(engine, "TEA") == 10 and stock(engine, "COF") == 5, "The first items' stock must not stay decremented."
    assert stock(engine, "PEN") == 95


def test_other_errors(engine):
    with Session(engine) as s:
        with pytest.raises(ValueError):
            place_order(s, 1, [])
        with pytest.raises(ValueError):
            place_order(s, 1, [("TEA", 0)])
        with pytest.raises(ValueError):
            place_order(s, 1, [("TEA", -1)])
        with pytest.raises(LookupError):
            place_order(s, 99, [("TEA", 1)])
        with pytest.raises(LookupError):
            place_order(s, 1, [("NOPE", 1)])
    assert stock(engine, "TEA") == 10


def test_a_stale_session_cannot_oversell(engine):
    a, b = Session(engine), Session(engine)
    try:
        stale = a.scalar(select(Product).where(Product.sku == "MUG"))
        assert stale.stock == 3                       # session a believes there are 3 mugs
        place_order(b, 2, [("MUG", 3)])               # session b takes all of them
        with pytest.raises(OutOfStock):
            place_order(a, 1, [("MUG", 1)])           # a's loaded object is stale; the database must refuse
    finally:
        a.close()
        b.close()
    assert stock(engine, "MUG") == 0


# ---- queries ------------------------------------------------------------------------------------------------

def test_orders_with_totals_in_one_statement(engine):
    with Session(engine) as s:
        for i in range(12):
            place_order(s, 1 + i % 3, [("PEN", i + 1), ("BOOK", 1)])
    with Session(engine) as s:
        log = QueryLog(engine)
        rows = orders_with_totals(s)
        assert log.count == 1, f"One statement, not {log.count}: join and group by in the database."
        assert len(rows) == 12
        assert rows[0] == (1, "Asha", 500 * 1 + 15000, 2)
        assert rows[1] == (2, "Ravi", 500 * 2 + 15000, 2)
        stored = {o.id: o.total_paise for o in s.scalars(select(Order))}
        assert all(total == stored[oid] for oid, _, total, _ in rows), "The totals computed from the lines must equal the stored ones."


# ---- backup -------------------------------------------------------------------------------------------------

def test_backup_and_restore_drill(engine, tmp_path):
    with Session(engine) as s:
        place_order(s, 1, [("TEA", 2), ("COF", 1)])
        place_order(s, 2, [("PEN", 10)])
    src = str(tmp_path / "shop.db")
    live = sqlite3.connect(src)
    expected = fingerprint(live)
    live.close()
    bak = str(tmp_path / "shop.bak")
    backup(src, bak)
    got = restore_and_verify(bak, expected, str(tmp_path / "restored.db"))
    assert got == expected
    assert expected["orders"]["rows"] == 2 and expected["order_lines"]["rows"] == 3


def test_restore_detects_a_stale_expectation_and_a_bad_file(engine, tmp_path):
    src = str(tmp_path / "shop.db")
    bak = str(tmp_path / "shop.bak")
    backup(src, bak)
    with Session(engine) as s:
        place_order(s, 1, [("TEA", 1)])
    live = sqlite3.connect(src)
    newer = fingerprint(live)
    live.close()
    with pytest.raises(RestoreFailed) as e:
        restore_and_verify(bak, newer, str(tmp_path / "r.db"))
    assert "orders" in str(e.value)
    open(str(tmp_path / "bad.bak"), "wb").write(b"junk" * 100)
    with pytest.raises(RestoreFailed):
        restore_and_verify(str(tmp_path / "bad.bak"), newer, str(tmp_path / "r2.db"))
    with pytest.raises(FileExistsError):
        backup(src, bak)
