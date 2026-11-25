import re

import pandas as pd
from solution import june_revenue


class Spy:
    """Wraps a connection and records the SQL text the solution runs."""

    def __init__(self, con):
        self._con = con
        self.log = []

    def execute(self, sql, *a, **k):
        self.log.append(str(sql))
        return self._con.execute(sql, *a, **k)

    def sql(self, sql, *a, **k):
        self.log.append(str(sql))
        return self._con.sql(sql, *a, **k)

    def __getattr__(self, name):
        return getattr(self._con, name)


def write(tmp_path, times, amounts):
    df = pd.DataFrame({"order_id": range(1, len(times) + 1), "user_id": range(1, len(times) + 1),
                       "order_time": pd.to_datetime(times), "plan": "monthly", "amount": amounts, "note": ["x" * 20] * len(times)})
    p = tmp_path / "orders.parquet"
    df.to_parquet(p, index=False)
    return str(p)


def test_boundaries(con, tmp_path):
    path = write(tmp_path, ["2025-05-31 23:59:59", "2025-06-01 00:00:00", "2025-06-15 12:00:00", "2025-06-30 23:59:59", "2025-07-01 00:00:00"],
                 [499, 3999, 499, 499, 3999])
    assert june_revenue(con, path) == 4997, "June = from 2025-06-01 00:00:00 up to but not including 2025-07-01 00:00:00: the 30 June 23:59:59 order is in, the 1 July midnight order is out."


def test_empty_month_is_zero(con, tmp_path):
    path = write(tmp_path, ["2025-05-01", "2025-07-02"], [10, 20])
    assert june_revenue(con, path) == 0, "No order in June: return 0 (sum of nothing is NULL: use COALESCE)."


def test_sql_is_pruned(con, tmp_path):
    path = write(tmp_path, ["2025-06-02", "2025-06-03"], [5, 7])
    spy = Spy(con)
    assert june_revenue(spy, path) == 12
    text = " ".join(spy.log).lower()
    assert "read_parquet" in text, "Read the file with read_parquet(...) inside the SQL."
    assert not re.search(r"select\s+\*", text), "Do not SELECT * from the file: name the columns you need (amount, order_time)."


def test_connection_is_still_usable(con, tmp_path):
    path = write(tmp_path, ["2025-06-02"], [5])
    june_revenue(con, path)
    assert con.execute("SELECT 1").fetchall() == [(1,)], "Do not leave a result open on the connection (no fetchone)."
