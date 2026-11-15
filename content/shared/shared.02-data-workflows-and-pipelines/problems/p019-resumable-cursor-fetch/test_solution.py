import hashlib
import json
import os
import sqlite3

import httpx
import pytest

from solution import fetch_resumable

BASE = "https://api.pagebound.test"


def token(offset):
    return hashlib.sha1(f"pagebound-{offset}".encode()).hexdigest()[:10]


def make_orders(n, first_id=201):
    return [{"id": first_id + i, "customer": {"email": f"c{i}@example.com", "city": None},
             "status": "shipped", "amount": "9.50", "currency": "INR",
             "created_at": "2024-06-01T10:00:00Z", "updated_at": f"2024-06-01T10:{i:02d}:00Z",
             "items": []} for i in range(n)]


class FakeCursorAPI:
    """Cursor API over a list of orders. fail_on: 1-based request numbers that fail."""

    def __init__(self, orders, fail_on=(), fail_with="connect"):
        self.orders = orders
        self.fail_on = set(fail_on)
        self.fail_with = fail_with
        self.requests = []

    def handler(self, request):
        params = dict(request.url.params)
        self.requests.append(params)
        if len(self.requests) in self.fail_on:
            if self.fail_with == "connect":
                raise httpx.ConnectError("simulated crash", request=request)
            return httpx.Response(500, json={"error": "server exploded"})
        limit = int(params["limit"])
        offsets = {token(o): o for o in range(0, len(self.orders) + limit, limit)}
        if "cursor" in params and params["cursor"] not in offsets:
            return httpx.Response(400, json={"error": "unknown cursor"})
        start = offsets[params["cursor"]] if "cursor" in params else 0
        items = self.orders[start:start + limit]
        nxt = token(start + limit) if start + limit < len(self.orders) else None
        return httpx.Response(200, json={"items": items, "next_cursor": nxt})

    def client(self):
        return httpx.Client(transport=httpx.MockTransport(self.handler), base_url=BASE)


def rows(db):
    conn = sqlite3.connect(db)          # a NEW connection sees only committed data
    try:
        return conn.execute("SELECT id, status FROM orders ORDER BY id").fetchall()
    finally:
        conn.close()


def run(api, db, cp, limit=3):
    conn = sqlite3.connect(db)
    try:
        return fetch_resumable(api.client(), conn, cp, limit=limit)
    finally:
        conn.close()                    # like a process dying: uncommitted work is lost


def cursors(requests):
    return [r.get("cursor") for r in requests]


def test_full_run(tmp_path):
    api = FakeCursorAPI(make_orders(8))
    db, cp = tmp_path / "o.db", tmp_path / "state" / "cp.json"
    n = run(api, db, cp)
    assert n == 8, f"Returned {n}; all 8 orders were written."
    assert cursors(api.requests) == [None, token(3), token(6)], (
        "Expected 3 requests: the first without a cursor, then each next_cursor exactly as the "
        "server sent it."
    )
    assert all(r["limit"] == "3" for r in api.requests), "Send limit on every request."
    assert [i for i, _ in rows(db)] == list(range(201, 209)), "All 8 orders must be committed."
    assert not cp.exists(), "After the last page the checkpoint must be deleted."


def test_crash_on_the_last_page_then_resume(tmp_path):
    api = FakeCursorAPI(make_orders(8), fail_on={3})
    db, cp = tmp_path / "o.db", tmp_path / "state" / "cp.json"
    with pytest.raises(httpx.ConnectError):
        run(api, db, cp)
    assert len(rows(db)) == 6, (
        f"{len(rows(db))} orders are committed after the crash on page 3; pages 1 and 2 (6 "
        "orders) must be. Commit after EACH page, not once at the end."
    )
    assert json.loads(cp.read_text(encoding="utf-8")) == {"cursor": token(6)}, (
        "After page 2 the checkpoint must hold page 2's next_cursor, so the resume asks for page 3."
    )
    api.fail_on.clear()
    before = len(api.requests)
    n = run(api, db, cp)
    assert cursors(api.requests[before:]) == [token(6)], (
        f"The resume sent cursors {cursors(api.requests[before:])}. It must start from the "
        "checkpoint's cursor and need only 1 request, not start again from the beginning."
    )
    assert n == 2, f"The resume returned {n}; it wrote only the 2 orders of the last page."
    assert [i for i, _ in rows(db)] == list(range(201, 209)), "After the resume all 8 orders, once each."
    assert not cp.exists(), "The finished resume must delete the checkpoint."


def test_crash_on_page_two_then_resume(tmp_path):
    api = FakeCursorAPI(make_orders(8), fail_on={2})
    db, cp = tmp_path / "o.db", tmp_path / "cp.json"
    with pytest.raises(httpx.ConnectError):
        run(api, db, cp)
    assert len(rows(db)) == 3
    api.fail_on.clear()
    before = len(api.requests)
    assert run(api, db, cp) == 5, "Resuming at page 2 writes pages 2 and 3: 3 + 2 = 5 orders."
    assert cursors(api.requests[before:]) == [token(3), token(6)]
    assert len(rows(db)) == 8


def test_crash_on_the_first_request(tmp_path):
    api = FakeCursorAPI(make_orders(8), fail_on={1})
    db, cp = tmp_path / "o.db", tmp_path / "cp.json"
    with pytest.raises(httpx.ConnectError):
        run(api, db, cp)
    assert not cp.exists(), "Nothing was loaded, so there must be no checkpoint yet."
    api.fail_on.clear()
    assert run(api, db, cp) == 8, "With no checkpoint the next run is a normal full run."


def test_http_500_is_a_crash_too(tmp_path):
    api = FakeCursorAPI(make_orders(8), fail_on={2}, fail_with="500")
    db, cp = tmp_path / "o.db", tmp_path / "cp.json"
    with pytest.raises(httpx.HTTPStatusError):
        run(api, db, cp)
    assert json.loads(cp.read_text(encoding="utf-8")) == {"cursor": token(3)}, (
        "A 500 must stop the run (raise_for_status) and keep the last good checkpoint."
    )


def test_crash_while_saving_the_checkpoint(tmp_path, monkeypatch):
    api = FakeCursorAPI(make_orders(8))
    db, cp = tmp_path / "o.db", tmp_path / "cp.json"
    real_replace = os.replace
    calls = []

    def flaky_replace(src, dst):
        calls.append(dst)
        if len(calls) == 2:
            raise OSError("simulated crash while saving the 2nd checkpoint")
        real_replace(src, dst)

    monkeypatch.setattr(os, "replace", flaky_replace)
    with pytest.raises(OSError):
        run(api, db, cp)
    monkeypatch.undo()
    assert len(calls) == 2, (
        f"os.replace was called {len(calls)} times. Save each checkpoint atomically with "
        "os.replace (temp file, then os.replace), once per page that has a next_cursor."
    )
    assert len(rows(db)) == 6, (
        f"{len(rows(db))} orders committed. The 2nd checkpoint save crashed AFTER page 2 should "
        "already be committed: write (and commit) the data FIRST, then the checkpoint."
    )
    assert json.loads(cp.read_text(encoding="utf-8")) == {"cursor": token(3)}, (
        "The failed save must leave the previous checkpoint (after page 1) intact."
    )
    before = len(api.requests)
    assert run(api, db, cp) == 5, "The resume starts at page 2 again and writes pages 2 and 3."
    assert cursors(api.requests[before:]) == [token(3), token(6)]
    assert [i for i, _ in rows(db)] == list(range(201, 209)), (
        "Page 2 was loaded twice (once before the crash, once on resume). The upsert must make "
        "that harmless: 8 orders, no duplicates, no IntegrityError."
    )


def test_replayed_page_updates_changed_orders(tmp_path):
    orders = make_orders(8)
    api = FakeCursorAPI(orders)
    db, cp = tmp_path / "o.db", tmp_path / "cp.json"
    run(api, db, cp)
    orders[4]["status"] = "cancelled"              # order 205 changes on the server
    cp.write_text(json.dumps({"cursor": token(3)}), encoding="utf-8")   # an old checkpoint
    assert run(api, db, cp) == 5
    assert (205, "cancelled") in rows(db), (
        "A re-fetched page must UPDATE existing rows (ON CONFLICT DO UPDATE), not ignore them."
    )
    assert len(rows(db)) == 8


def test_two_crashes_in_a_row(tmp_path):
    api = FakeCursorAPI(make_orders(8), fail_on={2, 4})
    db, cp = tmp_path / "o.db", tmp_path / "cp.json"
    with pytest.raises(httpx.ConnectError):
        run(api, db, cp)                            # request 1 ok, request 2 fails
    with pytest.raises(httpx.ConnectError):
        run(api, db, cp)                            # request 3 (page 2) ok, request 4 (page 3) fails
    assert json.loads(cp.read_text(encoding="utf-8")) == {"cursor": token(6)}, (
        "The second, partial run must move the checkpoint forward to page 3."
    )
    assert run(api, db, cp) == 2, "The third run only needs page 3 (2 orders)."
    assert cursors(api.requests) == [None, token(3), token(3), token(6), token(6)], (
        f"Requests over the three runs: {cursors(api.requests)}."
    )
    assert len(rows(db)) == 8


def test_next_run_after_success_is_a_fresh_full_run(tmp_path):
    api = FakeCursorAPI(make_orders(8))
    db, cp = tmp_path / "o.db", tmp_path / "cp.json"
    run(api, db, cp)
    before = len(api.requests)
    assert run(api, db, cp) == 8, "The checkpoint was deleted, so the next run reads everything again."
    assert cursors(api.requests[before:])[0] is None, "A fresh run starts without a cursor."
    assert len(rows(db)) == 8, "Re-running must not duplicate anything."


def test_other_page_size(tmp_path):
    api = FakeCursorAPI(make_orders(10, first_id=1), fail_on={3})
    db, cp = tmp_path / "o.db", tmp_path / "cp.json"
    with pytest.raises(httpx.ConnectError):
        run(api, db, cp, limit=4)
    assert len(rows(db)) == 8
    api.fail_on.clear()
    assert run(api, db, cp, limit=4) == 2
    assert [i for i, _ in rows(db)] == list(range(1, 11))
    assert all(r["limit"] == "4" for r in api.requests), "Pass the limit argument to the API."
