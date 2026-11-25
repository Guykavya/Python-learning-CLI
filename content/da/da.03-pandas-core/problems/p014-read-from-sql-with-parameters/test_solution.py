import sqlite3

import pandas as pd
import pytest

from solution import orders_since

ROWS = [
    (1, "Asha", "2024-02-28", 2),
    (2, "O'Brien", "2024-03-01", 5),
    (3, "Ben", "2024-03-01", 1),
    (4, "Asha", "2024-03-15", 4),
    (5, "O'Brien", "2024-04-02", 3),
    (6, "x' OR '1'='1", "2024-04-03", 9),
]


@pytest.fixture
def con():
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE orders(order_id INTEGER, customer TEXT, order_date TEXT, qty INTEGER)")
    c.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", ROWS)
    c.commit()
    yield c
    c.close()


def test_filter_by_date(con):
    out = orders_since(con, "2024-03-01")
    assert out["order_id"].tolist() == [2, 3, 4, 5, 6], "orders on or after 2024-03-01, sorted by date then id; got %s." % out["order_id"].tolist()
    assert out.columns.tolist() == ["order_id", "customer", "order_date", "qty"]
    assert out.index.tolist() == [0, 1, 2, 3, 4]


def test_dates_are_parsed(con):
    out = orders_since(con, "2024-03-01")
    assert pd.api.types.is_datetime64_any_dtype(out["order_date"]), "order_date dtype is %s: use parse_dates=['order_date']." % out["order_date"].dtype
    assert out["order_date"].iloc[0] == pd.Timestamp("2024-03-01")


def test_sorted_by_date_then_id(con):
    out = orders_since(con, "2024-01-01")
    assert out["order_id"].tolist() == [1, 2, 3, 4, 5, 6]
    shuffled = sqlite3.connect(":memory:")
    shuffled.execute("CREATE TABLE orders(order_id INTEGER, customer TEXT, order_date TEXT, qty INTEGER)")
    shuffled.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", [ROWS[4], ROWS[2], ROWS[0], ROWS[1], ROWS[3]])
    got = orders_since(shuffled, "2024-01-01")["order_id"].tolist()
    shuffled.close()
    assert got == [1, 2, 3, 4, 5], "ORDER BY order_date, order_id: got %s." % got


def test_a_quote_in_the_value_is_fine(con):
    try:
        out = orders_since(con, "2024-01-01", customer="O'Brien")
    except Exception as exc:
        pytest.fail("a name with a quote broke the query (%s): pass it with params=, not an f-string." % type(exc).__name__)
    assert out["order_id"].tolist() == [2, 5], "only O'Brien's orders: got %s." % out["order_id"].tolist()


def test_hostile_value_is_just_a_name(con):
    out = orders_since(con, "2024-01-01", customer="x' OR '1'='1")
    assert out["order_id"].tolist() == [6], "the value is plain text: it matches the one customer with that odd name. Got %s." % out["order_id"].tolist()
    none = orders_since(con, "2024-01-01", customer="nobody' OR '1'='1")
    assert len(none) == 0, "string-built SQL returned every row (SQL injection): use params."


def test_since_is_a_parameter_too(con):
    out = orders_since(con, "2024-03-15' OR '1'='1")
    assert len(out) <= 3, "the date is a parameter as well; building the SQL by hand lets it change the query."


def test_empty_result_keeps_columns(con):
    out = orders_since(con, "2030-01-01")
    assert len(out) == 0 and out.columns.tolist() == ["order_id", "customer", "order_date", "qty"]
