import sqlite3

import pandas as pd
import pytest

from solution import QUERY

SCHEMA = "CREATE TABLE visits (visit_id INTEGER, technician TEXT, rating INTEGER);"
# (visit_id, technician, rating, why)
DATA = [
    (1, "Asha", 5, "Asha: one rating of 5 ..."),
    (2, "Asha", None, "... and two visits nobody rated: the average is 5.0; COALESCE(rating, 0) would give 1.67"),
    (3, "Asha", None, ""),
    (4, "Bala", 4, "Bala: 4 and 2, all rated, average 3.0"),
    (5, "Bala", 2, ""),
    (6, "Chitra", None, "Chitra: nobody rated her: AVG is NULL, rated is 0"),
    (7, "Chitra", None, ""),
    (8, "Dev", 3, "Dev: 3, 4, 4 -> 3.67 (rounding to 2 decimals)"),
    (9, "Dev", 4, ""),
    (10, "Dev", 4, ""),
]


def connect(data=DATA):
    con = sqlite3.connect(":memory:")
    con.execute(SCHEMA)
    con.executemany("INSERT INTO visits VALUES (?,?,?)", [r[:3] for r in data])
    return con


def run(con):
    try:
        cur = con.execute(QUERY)
    except (sqlite3.Error, sqlite3.Warning) as e:
        pytest.fail(f"SQLite rejected your query: {e}. Write exactly one SELECT.")
    return [d[0] for d in cur.description], cur.fetchall()


def test_columns_and_order():
    names, rows = run(connect())
    assert names == ["technician", "rated", "avg_rating"], "columns must be technician, rated, avg_rating. Got %s." % names
    assert [r[0] for r in rows] == ["Asha", "Bala", "Chitra", "Dev"], "one row per technician, sorted by technician. Got %s." % [r[0] for r in rows]


def test_average_skips_null():
    _, rows = run(connect())
    got = {r[0]: (r[1], r[2]) for r in rows}
    assert got["Asha"] == (1, 5.0), (
        "Asha has one rating (5) and two NULLs: AVG skips NULL, so the average is 5.0 and rated is 1. "
        "If you got 1.67 you replaced NULL by 0 (COALESCE(rating, 0)): a missing rating is not a rating of zero. Got %s." % (got["Asha"],))
    assert got["Bala"] == (2, 3.0), "Bala: ratings 4 and 2, average 3.0. Got %s." % (got["Bala"],)
    assert got["Dev"] == (3, 3.67), "Dev: (3 + 4 + 4) / 3 = 3.67 with ROUND(..., 2). Got %s." % (got["Dev"],)


def test_nobody_rated_is_null_not_zero():
    _, rows = run(connect())
    chitra = [r for r in rows if r[0] == "Chitra"][0]
    assert chitra[1] == 0, "COUNT(rating) is 0 for Chitra. Got %s." % (chitra[1],)
    assert chitra[2] is None, "when nobody rated, the average is unknown: NULL (None), not 0. Got %r." % (chitra[2],)


def test_matches_pandas_on_other_data():
    other = [(i, "T%d" % (i % 3), None if i % 4 == 0 else (i % 5) + 1, "") for i in range(1, 40)]
    _, rows = run(connect(other))
    df = pd.DataFrame([r[:3] for r in other], columns=["visit_id", "technician", "rating"])
    g = df.groupby("technician")["rating"].agg(["count", "mean"])
    want = [(t, int(r["count"]), round(float(r["mean"]), 2)) for t, r in g.iterrows()]
    assert rows == want, "the query must work on any data. Expected %s, got %s." % (want, rows)
