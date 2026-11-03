import sqlite3
import pytest
from solution import SCRIPT


def fresh():
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    try:
        con.executescript(SCRIPT)
    except sqlite3.Error as e:
        pytest.fail(f"SQLite rejected your SCRIPT: {e}")
    return con


def filled():
    con = fresh()
    try:
        con.executescript("""
            INSERT INTO customers VALUES (1, 'Asha'), (2, 'Ben'), (3, 'Chen');
            INSERT INTO orders VALUES (10, 1, '2024-01-05'), (11, 1, '2024-02-10'),
                                      (12, 2, '2024-02-11'), (13, 3, '2024-03-01');
        """)
    except sqlite3.Error as e:
        pytest.fail(f"Could not insert the test rows (check table and column names): {e}")
    return con


def test_columns():
    con = fresh()
    cols = lambda t: [r[1] for r in con.execute(f"PRAGMA table_info({t})")]
    assert cols("customers") == ["customer_id", "name"], "customers needs the columns customer_id, name."
    assert cols("orders") == ["order_id", "customer_id", "ordered"], "orders needs the columns order_id, customer_id, ordered."


def test_foreign_key_declared_with_cascade():
    con = fresh()
    fk = con.execute("PRAGMA foreign_key_list(orders)").fetchall()
    assert len(fk) == 1, "orders.customer_id must be declared as a FOREIGN KEY (REFERENCES customers(customer_id))."
    row = fk[0]
    assert row[2] == "customers" and row[3] == "customer_id" and row[4] == "customer_id", \
        "The foreign key must point at customers(customer_id)."
    assert row[6].upper() == "CASCADE", "Add ON DELETE CASCADE to the foreign key."


def test_orphan_insert_rejected():
    con = filled()
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO orders VALUES (99, 42, '2024-04-01')")


def test_cascade_deletes_children_only():
    con = filled()
    con.execute("DELETE FROM customers WHERE customer_id = 1")
    left = [r[0] for r in con.execute("SELECT order_id FROM orders ORDER BY order_id")]
    assert left == [12, 13], "Deleting customer 1 must delete exactly their orders (10, 11) and keep the others."
    assert [r[0] for r in con.execute("SELECT customer_id FROM customers ORDER BY 1")] == [2, 3]


def test_not_null_rules():
    con = filled()
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO orders VALUES (50, NULL, '2024-04-01')")
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO customers VALUES (9, NULL)")
