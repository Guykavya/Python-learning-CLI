import sqlite3

import httpx
import pytest

from solution import run_incremental

BASE = "https://api.pagebound.test"
STATE_SQL = "SELECT value FROM pipeline_state WHERE name = 'orders.updated_at'"


def order(id_, status, updated_at, amount="19.99"):
    return {
        "id": id_, "customer": {"email": f"user{id_}@example.com", "city": "Pune"},
        "status": status, "amount": amount, "currency": "INR",
        "created_at": "2024-06-01T09:00:00Z", "updated_at": updated_at,
        "items": [{"sku": "B1", "qty": 1}],
    }


def initial_orders():
    # Sorted by id. The newest updated_at is 103's, NOT the last record's.
    return [
        order(101, "shipped", "2024-06-01T10:00:00Z"),
        order(102, "pending", "2024-06-01T11:00:00Z"),
        order(103, "shipped", "2024-06-03T09:00:00Z"),
        order(104, "pending", "2024-06-02T08:00:00Z"),
        order(105, "cancelled", "2024-06-01T12:00:00Z"),
    ]


class FakeAPI:
    """Page-number API with updated_since (strict >). Records every request's params."""

    def __init__(self, records, fail_on=(), fail_with="connect"):
        self.records = records
        self.requests = []
        self.fail_on = set(fail_on)      # 1-based request numbers that fail
        self.fail_with = fail_with

    def handler(self, request):
        params = dict(request.url.params)
        self.requests.append(params)
        if len(self.requests) in self.fail_on:
            if self.fail_with == "connect":
                raise httpx.ConnectError("simulated network failure", request=request)
            return httpx.Response(500, json={"error": "boom"})
        rows = sorted(self.records, key=lambda r: r["id"])
        since = params.get("updated_since")
        if since is not None:
            rows = [r for r in rows if r["updated_at"] > since]
        page, per_page = int(params.get("page", "1")), int(params.get("per_page", "3"))
        chunk = rows[(page - 1) * per_page: page * per_page]
        next_page = page + 1 if page * per_page < len(rows) else None
        return httpx.Response(200, json={"data": chunk, "page": page, "next_page": next_page})

    def client(self):
        return httpx.Client(transport=httpx.MockTransport(self.handler), base_url=BASE)


def orders_table(conn):
    return conn.execute("SELECT id, status, updated_at FROM orders ORDER BY id").fetchall()


def watermark(conn):
    row = conn.execute(STATE_SQL).fetchone()
    return row[0] if row else None


def test_first_run_loads_everything_without_updated_since():
    api = FakeAPI(initial_orders())
    conn = sqlite3.connect(":memory:")
    n = run_incremental(api.client(), conn)
    assert n == 5, f"Returned {n}; the API holds 5 orders and the first run must load them all."
    assert [p.get("page") for p in api.requests] == ["1", "2"], (
        f"Requested pages {[p.get('page') for p in api.requests]}; with per_page=3 and 5 orders "
        "you need page 1 and page 2, then stop when next_page is null."
    )
    assert all("updated_since" not in p for p in api.requests), (
        "The first run has no watermark, so do not send updated_since at all (not even "
        "updated_since=None or an empty string)."
    )
    assert all(p.get("per_page") == "3" for p in api.requests), "Send per_page on every request."
    assert [row[0] for row in orders_table(conn)] == [101, 102, 103, 104, 105]


def test_watermark_is_the_largest_updated_at_not_the_last_record():
    api = FakeAPI(initial_orders())
    conn = sqlite3.connect(":memory:")
    run_incremental(api.client(), conn)
    assert watermark(conn) == "2024-06-03T09:00:00Z", (
        f"Watermark is {watermark(conn)!r}. The API sorts by id, so the last record (105, "
        "06-01T12:00) is not the newest. Use max(updated_at) over everything received: 103's "
        "2024-06-03T09:00:00Z. Store it in pipeline_state under name 'orders.updated_at'."
    )


def test_second_run_without_changes_loads_zero():
    api = FakeAPI(initial_orders())
    conn = sqlite3.connect(":memory:")
    run_incremental(api.client(), conn)
    before, first_requests = orders_table(conn), len(api.requests)
    n = run_incremental(api.client(), conn)
    second = api.requests[first_requests:]
    assert n == 0, (
        f"The second run returned {n}. Nothing changed, so an incremental run must load 0. "
        "If it reloaded orders, the watermark was wrong or was not sent."
    )
    assert second == [{"page": "1", "per_page": "3", "updated_since": "2024-06-03T09:00:00Z"}], (
        f"Second run sent {second}. Expected exactly one request with updated_since set to "
        "the stored watermark."
    )
    assert orders_table(conn) == before, "A run with no new data must not change the orders."
    assert watermark(conn) == "2024-06-03T09:00:00Z", "No data received: keep the old watermark."


def test_changed_and_new_orders_are_picked_up():
    records = initial_orders()
    api = FakeAPI(records)
    conn = sqlite3.connect(":memory:")
    run_incremental(api.client(), conn)
    records[1] = order(102, "cancelled", "2024-06-04T10:00:00Z")   # changed on the server
    records.append(order(106, "pending", "2024-06-03T15:00:00Z"))   # new
    n = run_incremental(api.client(), conn)
    assert n == 2, f"Returned {n}; exactly 102 (changed) and 106 (new) are newer than the watermark."
    table = orders_table(conn)
    assert (102, "cancelled", "2024-06-04T10:00:00Z") in table, (
        "Order 102 changed on the server; the upsert must replace its old row."
    )
    assert len(table) == 6, f"{len(table)} rows; 5 old + 1 new = 6, one row per id (no duplicates)."
    assert watermark(conn) == "2024-06-04T10:00:00Z", (
        f"Watermark {watermark(conn)!r}; the API returned 102 then 106 (id order). The newest is "
        "102's 2024-06-04T10:00:00Z, not the last record's."
    )
    assert run_incremental(api.client(), conn) == 0, (
        "A third run must load 0. If it reloaded 102, the watermark was taken from the last "
        "record instead of the maximum."
    )


def test_watermark_survives_a_new_connection(tmp_path):
    path = tmp_path / "pipeline.db"
    api = FakeAPI(initial_orders())
    conn = sqlite3.connect(path)
    run_incremental(api.client(), conn)
    conn.close()
    conn = sqlite3.connect(path)
    n = run_incremental(api.client(), conn)
    conn.close()
    assert n == 0, (
        "After reconnecting, the run loaded data again. The watermark must be COMMITTED to the "
        "pipeline_state table, not kept in a variable."
    )
    assert api.requests[-1].get("updated_since") == "2024-06-03T09:00:00Z"


def test_empty_source_first_run():
    api = FakeAPI([])
    conn = sqlite3.connect(":memory:")
    assert run_incremental(api.client(), conn) == 0, "An empty API gives 0 records."
    assert watermark(conn) is None, (
        "Nothing was received, so there is no watermark yet. Do not store None, '' or a made-up time."
    )
    api.records.extend(initial_orders())
    assert run_incremental(api.client(), conn) == 5, "Later data must still be loaded in full."
    assert "updated_since" not in api.requests[-1], "Still no watermark, so still no updated_since."


def test_failure_on_a_later_page_changes_nothing():
    api = FakeAPI(initial_orders(), fail_on={2})
    conn = sqlite3.connect(":memory:")
    with pytest.raises(httpx.ConnectError):
        run_incremental(api.client(), conn)
    assert orders_table(conn) == [], (
        "Page 2 failed, but page 1's orders are in the table. Data and watermark must change "
        "together in ONE transaction; a failed run must leave nothing (roll back)."
    )
    assert watermark(conn) is None, "A failed run must not store a watermark."
    api.fail_on.clear()
    assert run_incremental(api.client(), conn) == 5, "After the failure, a normal run loads all 5."
    assert "updated_since" not in api.requests[-1], (
        "The failed run must not have left a watermark behind, so the retry starts from scratch."
    )


def test_failure_in_an_incremental_run_keeps_the_old_watermark():
    records = initial_orders()
    records += [order(i, "pending", f"2024-06-05T0{i - 106}:00:00Z") for i in range(106, 110)]
    api = FakeAPI(records[:5])
    conn = sqlite3.connect(":memory:")
    run_incremental(api.client(), conn)
    api.records = records                       # 4 new orders arrive: 2 pages at per_page=3
    api.fail_on = {len(api.requests) + 2}       # the second page of the next run fails
    with pytest.raises(httpx.ConnectError):
        run_incremental(api.client(), conn)
    assert watermark(conn) == "2024-06-03T09:00:00Z", (
        "The run failed, so the watermark must stay at the last successful value. If it moved, "
        "the orders of the failed page would be skipped forever."
    )
    assert len(orders_table(conn)) == 5, "No order from the failed run may be stored."
    api.fail_on.clear()
    assert run_incremental(api.client(), conn) == 4, "The rerun must load the 4 new orders."
    assert watermark(conn) == "2024-06-05T03:00:00Z"


def test_http_errors_are_raised():
    api = FakeAPI(initial_orders(), fail_on={1}, fail_with="500")
    conn = sqlite3.connect(":memory:")
    with pytest.raises(httpx.HTTPStatusError):
        run_incremental(api.client(), conn)
    assert orders_table(conn) == [], "A 500 must stop the run; call raise_for_status()."


def test_per_page_is_used():
    api = FakeAPI(initial_orders())
    conn = sqlite3.connect(":memory:")
    assert run_incremental(api.client(), conn, per_page=2) == 5
    assert [p["page"] for p in api.requests] == ["1", "2", "3"], (
        "per_page=2 with 5 orders needs pages 1, 2, 3. Pass per_page to the API."
    )
    assert all(p["per_page"] == "2" for p in api.requests)
