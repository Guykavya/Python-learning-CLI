import sqlite3
import pytest

from solution import SCRIPT

BASE = """CREATE TABLE stock (book_id INTEGER PRIMARY KEY, qty INTEGER NOT NULL);
CREATE TABLE incoming (book_id INTEGER, qty INTEGER);
"""
A = BASE + """INSERT INTO stock VALUES (1,10),(2,0),(3,4);
INSERT INTO incoming VALUES (1,5),(2,3),(4,7),(4,1);"""
B = BASE + """INSERT INTO stock VALUES (5,0),(6,2),(7,0),(8,9);
INSERT INTO incoming VALUES (6,1),(6,1),(7,2),(9,4),(5,0);"""
C = BASE + """INSERT INTO stock VALUES (1,3);"""


def run(schema):
    con = sqlite3.connect(":memory:")
    con.executescript(schema)
    try:
        con.executescript(SCRIPT)
    except sqlite3.Error as e:
        pytest.fail(f"SQLite rejected your script: {e}")
    return con


def stock(con):
    return con.execute("SELECT book_id, qty FROM stock ORDER BY book_id").fetchall()


def test_dataset_a():
    assert stock(run(A)) == [(1, 15), (2, 3), (3, 4), (4, 8)], \
        "Expected (1,15) (2,3) (3,4) (4,8). Book 2 (qty 0) is deleted FIRST, then re-created with 3. Book 4 arrives twice: 7+1."


def test_dataset_b():
    assert stock(run(B)) == [(5, 0), (6, 4), (7, 2), (8, 9), (9, 4)], \
        "Book 5: deleted (qty 0), then re-created from the delivery of 0 (a row with qty 0). Book 6: 2+1+1. Book 7: deleted, then 2. Book 9 is new."


def test_no_deliveries_keeps_rows():
    assert stock(run(C)) == [(1, 3)], "With no deliveries the stock must stay as it is (and nothing with qty > 0 is deleted)."


def test_uses_upsert():
    s = SCRIPT.upper()
    assert "ON CONFLICT" in s and "EXCLUDED" in s, "Use INSERT ... ON CONFLICT (book_id) DO UPDATE SET qty = qty + excluded.qty."
