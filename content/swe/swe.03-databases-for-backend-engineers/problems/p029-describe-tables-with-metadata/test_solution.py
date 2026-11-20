import pytest
from sqlalchemy import Integer, MetaData, String, create_engine, inspect, insert, select
from sqlalchemy.exc import IntegrityError

from solution import make_tables


@pytest.fixture
def setup():
    metadata = MetaData()
    customers, orders = make_tables(metadata)
    engine = create_engine("sqlite://")
    metadata.create_all(engine)
    return engine, customers, orders


def cols(engine, table):
    return {c["name"]: c for c in inspect(engine).get_columns(table)}


def test_tables_are_on_the_given_metadata_and_created(setup):
    engine, customers, orders = setup
    assert set(inspect(engine).get_table_names()) == {"customers", "orders"}
    assert customers.name == "customers" and orders.name == "orders"


def test_customer_columns(setup):
    engine, *_ = setup
    c = cols(engine, "customers")
    assert set(c) == {"id", "name", "city", "email"}
    assert isinstance(c["name"]["type"], String) and c["name"]["type"].length == 100 and not c["name"]["nullable"]
    assert c["city"]["nullable"] and c["city"]["type"].length == 50, "city may be NULL."
    assert not c["email"]["nullable"] and c["email"]["type"].length == 200
    assert inspect(engine).get_pk_constraint("customers")["constrained_columns"] == ["id"]


def test_email_is_unique(setup):
    engine, customers, _ = setup
    with engine.begin() as conn:
        conn.execute(insert(customers), {"name": "A", "email": "a@x.com"})
    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(insert(customers), {"name": "B", "email": "a@x.com"})


def test_order_columns_and_foreign_key(setup):
    engine, *_ = setup
    c = cols(engine, "orders")
    assert set(c) == {"id", "customer_id", "total_paise", "status"}
    assert isinstance(c["total_paise"]["type"], Integer) and not c["total_paise"]["nullable"]
    assert not c["customer_id"]["nullable"]
    fks = inspect(engine).get_foreign_keys("orders")
    assert [(f["constrained_columns"], f["referred_table"], f["referred_columns"]) for f in fks] == [(["customer_id"], "customers", ["id"])]


def test_status_has_a_server_default(setup):
    engine, customers, orders = setup
    with engine.begin() as conn:
        conn.execute(insert(customers), {"name": "A", "email": "a@x.com"})
        conn.execute(insert(orders), {"customer_id": 1, "total_paise": 500})
        assert conn.execute(select(orders.c.status)).scalar_one() == "open", "Use server_default='open': the database fills it in."
    d = cols(engine, "orders")["status"]["default"]
    assert d is not None and "open" in str(d), "The DEFAULT must exist in the table definition itself."


def test_not_null_is_enforced(setup):
    engine, customers, orders = setup
    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(insert(customers), {"name": None, "email": "n@x.com"})
