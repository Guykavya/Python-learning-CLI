import copy
import json
import sqlite3

import httpx
import pytest

from solution import run

BASE = "https://api.pagebound.test"


def make_orders(ids):
    return [{"id": i, "customer": {"email": f"c{i}@example.com", "city": "Pune"},
             "status": "shipped", "amount": f"{i - 100}.50", "currency": "INR",
             "created_at": "2024-06-01T10:00:00Z", "updated_at": "2024-06-01T12:00:00Z",
             "items": [{"sku": "B1", "qty": 1}, {"sku": "B2", "qty": i % 3}]} for i in ids]


class FakeAPI:
    def __init__(self, orders):
        self.orders = orders
        self.broken = set()           # ids served with "items": null (a bad response)
        self.bad_amount = set()       # ids served with "amount": [..] (SQLite cannot store a list)
        self.fail_on = set()          # 1-based request numbers that raise ConnectError
        self.requests = []

    def handler(self, request):
        params = dict(request.url.params)
        self.requests.append(params)
        if len(self.requests) in self.fail_on:
            raise httpx.ConnectError("simulated network failure", request=request)
        page, per_page = int(params["page"]), int(params["per_page"])
        chunk = copy.deepcopy(self.orders[(page - 1) * per_page: page * per_page])
        for order in chunk:
            if order["id"] in self.broken:
                order["items"] = None
            if order["id"] in self.bad_amount:
                order["amount"] = [order["amount"]]
        next_page = page + 1 if page * per_page < len(self.orders) else None
        return httpx.Response(200, json={"data": chunk, "page": page, "next_page": next_page})

    def client(self):
        return httpx.Client(transport=httpx.MockTransport(self.handler), base_url=BASE)


def table(db):
    conn = sqlite3.connect(db)
    try:
        return conn.execute("SELECT id, status, amount, qty, updated_at FROM orders ORDER BY id").fetchall()
    finally:
        conn.close()


def ids(db):
    return [row[0] for row in table(db)]


def pages(requests):
    return [r["page"] for r in requests]


@pytest.fixture
def setup(tmp_path):
    api = FakeAPI(make_orders(range(101, 108)))
    return api, tmp_path / "orders.db", tmp_path / "cp.json"


def test_a_good_night_still_works(setup):
    api, db, cp = setup
    assert run(api.client(), db, cp) == 7, "A normal run loads all 7 orders."
    assert pages(api.requests) == ["1", "2", "3"]
    assert ids(db) == list(range(101, 108))
    assert table(db)[0] == (101, "shipped", "1.50", 3, "2024-06-01T12:00:00Z"), (
        "The columns must keep their names and values (qty = sum of item quantities)."
    )
    assert not cp.exists(), "After a successful run the checkpoint must still be deleted."


def test_incident_1_running_twice_does_not_duplicate(setup):
    api, db, cp = setup
    run(api.client(), db, cp)
    second = run(api.client(), db, cp)
    assert ids(db) == list(range(101, 108)), (
        f"After two runs the table has ids {ids(db)}. Every run APPENDS. Give the table a key "
        "(id INTEGER PRIMARY KEY) and write with an UPSERT so a re-run changes nothing."
    )
    assert second == 7, "The second run still reads and writes all 7 orders (it returns 7)."


def test_three_runs_still_seven_rows(setup):
    api, db, cp = setup
    for _ in range(3):
        run(api.client(), db, cp)
    assert len(table(db)) == 7, f"{len(table(db))} rows after three runs; it must stay 7."


def test_rerun_picks_up_changes(setup):
    api, db, cp = setup
    run(api.client(), db, cp)
    api.orders[1]["status"] = "cancelled"
    api.orders[1]["updated_at"] = "2024-06-02T08:00:00Z"
    run(api.client(), db, cp)
    row_102 = [row for row in table(db) if row[0] == 102]
    assert row_102 == [(102, "cancelled", "2.50", 1, "2024-06-02T08:00:00Z")], (
        f"Rows for 102: {row_102}. The re-run must UPDATE the existing row (ON CONFLICT DO "
        "UPDATE). INSERT OR IGNORE would keep the stale 'shipped'; plain INSERT duplicates it."
    )


def test_incident_2_crash_in_page_two_resumes_at_page_two(setup):
    api, db, cp = setup
    api.broken = {105}
    with pytest.raises(TypeError):
        run(api.client(), db, cp)
    assert json.loads(cp.read_text(encoding="utf-8")) == {"next_page": 2}, (
        f"After the crash while processing page 2 the checkpoint says "
        f"{cp.read_text(encoding='utf-8')}. It must still say page 2: page 2 was NOT stored. "
        "Saving the checkpoint BEFORE the data is written claims work that never happened. "
        "Write and commit the page first, then save the checkpoint."
    )
    assert ids(db) == [101, 102, 103], "Only page 1 was committed before the crash."
    api.broken = set()                                   # the API team fixes order 105
    before = len(api.requests)
    n = run(api.client(), db, cp)
    assert pages(api.requests[before:]) == ["2", "3"], (
        f"The re-run requested pages {pages(api.requests[before:])}; it must resume at page 2 "
        "(the page that failed) and continue to the end."
    )
    assert ids(db) == list(range(101, 108)), (
        f"After the resume the table has ids {ids(db)}; orders 104-106 must not be lost. If page "
        "1 vanished, do not 'fix' duplicates by deleting the table at the start of each run."
    )
    assert n == 4, f"The resume returned {n}; it loaded pages 2 and 3: 3 + 1 = 4 orders."
    assert not cp.exists()


def test_crash_while_writing_page_two_resumes_at_page_two(setup):
    api, db, cp = setup
    api.bad_amount = {105}                               # transform passes, the INSERT fails
    with pytest.raises(sqlite3.Error):
        run(api.client(), db, cp)
    assert json.loads(cp.read_text(encoding="utf-8")) == {"next_page": 2}, (
        f"The database write of page 2 failed, but the checkpoint says "
        f"{cp.read_text(encoding='utf-8')}. Moving save_checkpoint below transform is not enough: "
        "the checkpoint may only be saved AFTER the page is committed."
    )
    assert ids(db) == [101, 102, 103], "The failed page must be rolled back (with conn: does that)."
    api.bad_amount = set()
    before = len(api.requests)
    assert run(api.client(), db, cp) == 4
    assert pages(api.requests[before:]) == ["2", "3"]
    assert ids(db) == list(range(101, 108))


def test_crash_on_the_last_page(setup):
    api, db, cp = setup
    api.broken = {107}
    with pytest.raises(TypeError):
        run(api.client(), db, cp)
    assert json.loads(cp.read_text(encoding="utf-8")) == {"next_page": 3}, (
        "The crash happened while processing page 3, so the checkpoint must point at page 3."
    )
    api.broken = set()
    before = len(api.requests)
    assert run(api.client(), db, cp) == 1
    assert pages(api.requests[before:]) == ["3"]
    assert ids(db) == list(range(101, 108))


def test_network_crash_then_resume_then_full_rerun(setup):
    api, db, cp = setup
    api.fail_on = {2}
    with pytest.raises(httpx.ConnectError):
        run(api.client(), db, cp)
    api.fail_on = set()
    assert run(api.client(), db, cp) == 4, "Resume after the failed request for page 2: pages 2, 3."
    assert run(api.client(), db, cp) == 7, "The checkpoint is gone, so the next run is a full run."
    assert ids(db) == list(range(101, 108)), (
        "Crash, resume and a full re-run must still give exactly one row per order."
    )


def test_resume_does_not_duplicate_page_one(setup):
    api, db, cp = setup
    api.broken = {104}
    with pytest.raises(TypeError):
        run(api.client(), db, cp)
    api.broken = set()
    run(api.client(), db, cp)
    run(api.client(), db, cp)
    assert ids(db) == list(range(101, 108)), (
        f"Ids after crash + resume + re-run: {ids(db)}. Each order exactly once."
    )
