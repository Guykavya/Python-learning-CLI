import sqlite3
import pytest

from solution import SCRIPT

A = """CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT, joined TEXT);
CREATE TABLE city_list (city TEXT PRIMARY KEY);
INSERT INTO customers VALUES (1,'Ada','Pune','2023-01-10'),(2,'Bo','Pune','2023-02-11'),(3,'Cy','Oslo','2023-03-12'),(4,'Di',NULL,'2023-04-13');"""
B = """CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT, joined TEXT);
CREATE TABLE city_list (city TEXT PRIMARY KEY);
INSERT INTO customers VALUES (7,'Eve','Rome','2022-01-01'),(9,'Fay','Rome','2022-01-02'),(10,'Gus',NULL,'2022-01-03'),(11,'Hal',NULL,'2022-01-04'),(12,'Ivy','Lima','2022-01-05');"""


def run(schema):
    con = sqlite3.connect(":memory:")
    con.executescript(schema)
    try:
        con.executescript(SCRIPT)
    except sqlite3.Error as e:
        pytest.fail(f"SQLite rejected your script: {e}")
    return con


@pytest.mark.parametrize("schema, before", [(A, 4), (B, 5)])
def test_new_customers(schema, before):
    con = run(schema)
    n = con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    assert n == before + 2, f"customers should grow by exactly 2 rows (had {before}, now {n})."
    zoe = con.execute("SELECT name, city, joined FROM customers WHERE name = 'Zoe'").fetchall()
    yan = con.execute("SELECT name, city, joined FROM customers WHERE name = 'Yan'").fetchall()
    assert zoe == [("Zoe", "Lima", "2024-05-01")], f"Zoe's row is wrong: {zoe}"
    assert yan == [("Yan", None, "2024-05-02")], f"Yan's city must be a real NULL, not the text 'NULL': {yan}"


@pytest.mark.parametrize("schema", [A, B])
def test_city_list(schema):
    con = run(schema)
    expect = sorted(r[0] for r in con.execute("SELECT DISTINCT city FROM customers WHERE city IS NOT NULL"))
    got = sorted(r[0] for r in con.execute("SELECT city FROM city_list"))
    assert "Lima" in got, "Lima is missing: insert the new customers BEFORE filling city_list."
    assert got == expect, f"city_list should hold each distinct non-NULL city once: expected {expect}, got {got}. Did you type the names instead of using INSERT ... SELECT?"


def test_uses_insert_select():
    s = SCRIPT.upper()
    assert s.count("INSERT") >= 2 and "SELECT" in s, "Fill city_list with INSERT INTO ... SELECT."
