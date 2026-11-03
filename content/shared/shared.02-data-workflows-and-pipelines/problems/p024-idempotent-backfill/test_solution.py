import sqlite3
from datetime import date

import httpx
import pytest

from solution import backfill

BASE = "https://api.pagebound.test"

SCHEMA = """CREATE TABLE orders (
    id INTEGER PRIMARY KEY, order_date TEXT NOT NULL, status TEXT NOT NULL, amount TEXT NOT NULL)"""

OLD_ROWS = [
    (2, "2024-06-01", "pending", "5.00"),     # old version of order 2
    (4, "2024-06-02", "pending", "7.00"),     # old version of order 4
    (40, "2024-06-02", "shipped", "3.00"),    # deleted at the source since
    (90, "2024-06-03", "shipped", "1.00"),    # deleted at the source since
    (91, "2024-05-31", "shipped", "2.00"),    # outside the range: must never change
]

EXPECTED = [
    (1, "2024-06-01", "shipped", "1.50"),
    (2, "2024-06-01", "shipped", "2.50"),
    (3, "2024-06-01", "shipped", "3.50"),
    (4, "2024-06-02", "shipped", "4.50"),
    (5, "2024-06-02", "shipped", "5.50"),
    (6, "2024-06-02", "shipped", "6.50"),
    (91, "2024-05-31", "shipped", "2.00"),
]


def o(i, day, status="shipped", amount=None):
    return {"id": i, "customer": {"email": f"c{i}@example.com", "city": "Pune"}, "status": status,
            "amount": amount if amount is not None else f"{i}.50", "currency": "INR",
            "created_at": f"{day}T10:00:00Z", "updated_at": f"{day}T11:00:00Z", "items": []}


def default_pages():
    return {
        "2024-06-01": [[o(1, "2024-06-01"), o(2, "2024-06-01")], [o(3, "2024-06-01")]],
        "2024-06-02": [[o(4, "2024-06-02"), o(5, "2024-06-02")],
                       [o(5, "2024-06-02"), o(6, "2024-06-02")]],     # 5 again: the data shifted
        "2024-06-03": [],                                              # no orders any more
    }


class FakeAPI:
    def __init__(self, pages):
        self.pages = pages               # day -> list of pages (each a list of orders)
        self.fail_on = set()             # {(day, page)} raising ConnectError
        self.requests = []

    def handler(self, request):
        day, page = request.url.params["created_on"], int(request.url.params["page"])
        self.requests.append((day, page))
        if (day, page) in self.fail_on:
            raise httpx.ConnectError("simulated network failure", request=request)
        pages = self.pages.get(day, [])
        data = pages[page - 1] if page <= len(pages) else []
        next_page = page + 1 if page < len(pages) else None
        return httpx.Response(200, json={"data": data, "page": page, "next_page": next_page})

    def client(self):
        return httpx.Client(transport=httpx.MockTransport(self.handler), base_url=BASE)


def seeded(tmp_path, rows=OLD_ROWS):
    path = tmp_path / "orders.db"
    conn = sqlite3.connect(path)
    conn.execute(SCHEMA)
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", rows)
    conn.commit()
    return conn, path


def dump(conn):
    return conn.execute("SELECT id, order_date, status, amount FROM orders ORDER BY id").fetchall()


def committed(path):
    other = sqlite3.connect(path)
    try:
        return dump(other)
    finally:
        other.close()


JUNE_1, JUNE_3 = date(2024, 6, 1), date(2024, 6, 3)


def test_backfill_replaces_each_day(tmp_path):
    conn, path = seeded(tmp_path)
    api = FakeAPI(default_pages())
    counts = backfill(api.client(), conn, JUNE_1, JUNE_3)
    assert counts == {"2024-06-01": 3, "2024-06-02": 3, "2024-06-03": 0}, (
        f"Returned {counts}. Count the orders STORED per day: order 5 appears on two pages of "
        "06-02 but is one order, and 06-03 has none (end is included)."
    )
    assert list(counts) == ["2024-06-01", "2024-06-02", "2024-06-03"], "Keys in day order."
    table = committed(path)
    assert table == EXPECTED, (
        f"Table after the backfill:\n{table}\nExpected:\n{EXPECTED}\n"
        "Orders 40 and 90 were deleted at the source, so deleting each day before inserting must "
        "remove them; order 2 and 4 get their new values; order 91 (05-31) is outside the range."
    )


def test_requests_every_page_of_every_day(tmp_path):
    conn, _ = seeded(tmp_path)
    api = FakeAPI(default_pages())
    backfill(api.client(), conn, JUNE_1, JUNE_3)
    assert api.requests == [("2024-06-01", 1), ("2024-06-01", 2), ("2024-06-02", 1),
                            ("2024-06-02", 2), ("2024-06-03", 1)], (
        f"Requests were {api.requests}. Walk the days in order, start and end included, and "
        "follow next_page for each day."
    )


def test_running_twice_gives_the_same_table(tmp_path):
    conn, path = seeded(tmp_path)
    api = FakeAPI(default_pages())
    first = backfill(api.client(), conn, JUNE_1, JUNE_3)
    after_first = committed(path)
    second = backfill(api.client(), conn, JUNE_1, JUNE_3)
    assert committed(path) == after_first == EXPECTED, (
        "The second backfill of the same range changed the table. Delete + insert per day must "
        "be idempotent."
    )
    assert second == first


def test_crash_while_fetching_a_day_keeps_its_old_rows(tmp_path):
    conn, path = seeded(tmp_path)
    api = FakeAPI(default_pages())
    api.fail_on = {("2024-06-02", 2)}
    with pytest.raises(httpx.ConnectError):
        backfill(api.client(), conn, JUNE_1, JUNE_3)
    table = committed(path)
    day2 = [row for row in table if row[1] == "2024-06-02"]
    assert day2 == [(4, "2024-06-02", "pending", "7.00"), (40, "2024-06-02", "shipped", "3.00")], (
        f"06-02 holds {day2} after the network failed on its page 2. Fetch ALL pages of a day "
        "before touching the table: a failed fetch must leave the day's old rows (not half a "
        "day, not an empty day)."
    )
    day1 = [row[0] for row in table if row[1] == "2024-06-01"]
    assert day1 == [1, 2, 3], "06-01 finished before the crash; it must be committed."
    assert (90, "2024-06-03", "shipped", "1.00") in table, "06-03 was not reached; it must be untouched."
    api.fail_on = set()
    backfill(api.client(), conn, JUNE_1, JUNE_3)
    assert committed(path) == EXPECTED, "Re-running the range after the crash must repair it completely."


def test_crash_while_writing_a_day_rolls_it_back(tmp_path):
    conn, _ = seeded(tmp_path)
    pages = default_pages()
    pages["2024-06-02"][1][1]["amount"] = None                     # order 6 is broken: amount null
    api = FakeAPI(pages)
    with pytest.raises(sqlite3.IntegrityError):
        backfill(api.client(), conn, JUNE_1, JUNE_3)
    day2 = [row for row in dump(conn) if row[1] == "2024-06-02"]
    assert day2 == [(4, "2024-06-02", "pending", "7.00"), (40, "2024-06-02", "shipped", "3.00")], (
        f"06-02 holds {day2} after an INSERT failed (amount NULL). DELETE and INSERT must be in "
        "ONE transaction ('with conn:'), so a failure rolls the delete back. Also store amount as "
        "given (None must reach SQLite as NULL, not the string 'None')."
    )
    assert [row[0] for row in dump(conn) if row[1] == "2024-06-01"] == [1, 2, 3]


def test_start_after_end(tmp_path):
    conn, _ = seeded(tmp_path)
    api = FakeAPI(default_pages())
    with pytest.raises(ValueError):
        backfill(api.client(), conn, JUNE_3, JUNE_1)
    assert api.requests == [], "Check the range BEFORE sending any request."


def test_single_day(tmp_path):
    conn, path = seeded(tmp_path)
    api = FakeAPI(default_pages())
    counts = backfill(api.client(), conn, date(2024, 6, 2), date(2024, 6, 2))
    assert counts == {"2024-06-02": 3}
    assert {day for day, _ in api.requests} == {"2024-06-02"}
    table = committed(path)
    assert (2, "2024-06-01", "pending", "5.00") in table and (90, "2024-06-03", "shipped", "1.00") in table, (
        "Only the requested day may change."
    )


def test_order_moved_to_another_day(tmp_path):
    conn, path = seeded(tmp_path, OLD_ROWS + [(7, "2024-05-30", "shipped", "9.00")])
    pages = default_pages()
    pages["2024-06-01"][1].append(o(7, "2024-06-01", status="cancelled"))   # 7's date was corrected
    api = FakeAPI(pages)
    counts = backfill(api.client(), conn, JUNE_1, JUNE_1)
    rows_7 = [row for row in committed(path) if row[0] == 7]
    assert rows_7 == [(7, "2024-06-01", "cancelled", "7.50")], (
        f"Rows for order 7: {rows_7}. It was stored under 05-30 and the source now lists it under "
        "06-01. A plain INSERT fails on the primary key and INSERT OR IGNORE keeps the old day: "
        "upsert it (ON CONFLICT DO UPDATE, including order_date) or INSERT OR REPLACE."
    )
    assert counts == {"2024-06-01": 4}


def test_month_boundary_and_empty_days(tmp_path):
    conn, _ = seeded(tmp_path, [])
    pages = {"2024-02-28": [[o(1, "2024-02-28")]], "2024-03-01": [[o(2, "2024-03-01")]]}
    api = FakeAPI(pages)
    counts = backfill(api.client(), conn, date(2024, 2, 28), date(2024, 3, 1))
    assert counts == {"2024-02-28": 1, "2024-02-29": 0, "2024-03-01": 1}, (
        f"Returned {counts}. 2024 is a leap year: walk real dates with timedelta(days=1), do not "
        "build the strings by hand."
    )


def test_creates_the_table(tmp_path):
    conn = sqlite3.connect(tmp_path / "new.db")
    api = FakeAPI(default_pages())
    assert backfill(api.client(), conn, JUNE_1, JUNE_1) == {"2024-06-01": 3}, (
        "On an empty database, create the table (CREATE TABLE IF NOT EXISTS) first."
    )
