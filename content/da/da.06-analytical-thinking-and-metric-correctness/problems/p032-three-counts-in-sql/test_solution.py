import sqlite3

import pandas as pd
import pytest

from solution import QUERY

SCHEMA = "CREATE TABLE payments (payment_id INTEGER, customer_id INTEGER, method TEXT, amount INTEGER, paid_at TEXT);"
# (payment_id, customer_id, method, amount, paid_at): one row per rule
DATA = [
    (1, 10, "upi", 500, "2025-02-01 10:00:00"),     # customer 10, method recorded
    (2, 10, None, 300, "2025-02-02 10:00:00"),      # same customer again, method NOT recorded
    (3, 11, "card", 200, "2025-02-03 10:00:00"),    # customer 11
    (4, 12, "upi", 400, "2025-02-03 11:00:00"),     # customer 12
    (5, None, "cash", 100, "2025-02-04 10:00:00"),  # no customer recorded: a row and a method, not a customer
    (6, 11, "", 250, "2025-02-05 10:00:00"),        # empty text is a value, not NULL
    (7, 12, None, 150, "2025-02-06 10:00:00"),      # customer 12 again, no method
]


def connect(rows):
    con = sqlite3.connect(":memory:")
    con.execute(SCHEMA)
    con.executemany("INSERT INTO payments VALUES (?,?,?,?,?)", rows)
    return con


def run(con):
    try:
        cur = con.execute(QUERY)
    except (sqlite3.Error, sqlite3.Warning) as e:
        pytest.fail(f"SQLite rejected your query: {e}. Write exactly one SELECT statement.")
    return [d[0] for d in cur.description], cur.fetchall()


def truth(rows):
    df = pd.DataFrame(rows, columns=["payment_id", "customer_id", "method", "amount", "paid_at"])
    return (len(df), int(df["method"].count()), int(df["customer_id"].nunique()))


def test_columns_names_and_order():
    names, rows = run(connect(DATA))
    assert names == ["rows", "with_method", "distinct_customers"], "name the three columns with AS: rows, with_method, distinct_customers. Got %s." % names
    assert len(rows) == 1, "return exactly one row (an aggregate without GROUP BY). Got %d rows." % len(rows)


def test_the_three_counts():
    names, rows = run(connect(DATA))
    assert truth(DATA) == (7, 5, 3), "the test data was counted by hand: 7 rows, 5 methods (the empty text counts), 3 customers."
    assert rows[0] == (7, 5, 3), (
        "expected rows=7, with_method=5, distinct_customers=3. COUNT(*) counts rows, COUNT(method) skips NULL "
        "(an empty text '' is NOT NULL), COUNT(DISTINCT customer_id) counts different non-NULL values. Got %s." % (rows[0],))


def test_all_null_and_empty_table():
    only_null = [(1, None, None, 10, "2025-02-01 00:00:00"), (2, None, None, 20, "2025-02-02 00:00:00")]
    _, rows = run(connect(only_null))
    assert rows[0] == (2, 0, 0), "two rows with every method and customer NULL: (2, 0, 0). Got %s." % (rows[0],)
    _, rows = run(connect([]))
    assert rows[0] == (0, 0, 0), "an empty table gives one row of zeros (COUNT never returns NULL). Got %s." % (rows[0],)


def test_matches_pandas_on_other_data():
    other = [(i, i % 4 if i % 5 else None, "upi" if i % 3 else None, 10, "2025-03-01 00:00:00") for i in range(1, 31)]
    _, rows = run(connect(other))
    assert rows[0] == truth(other), "the query must work on any data, not just the example. Got %s, pandas says %s." % (rows[0], truth(other))
