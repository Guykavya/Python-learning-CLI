import hashlib
import hmac
import json
import logging
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import httpx
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

import solution
from solution import (BadRecord, load_checkpoint, load_secret, run_pipeline, save_checkpoint,
                      transform)

BASE = "https://api.pagebound.test"
FIXTURES = Path(__file__).parent / "fixtures"
SECRET = b"unit-test-secret-0123456789"
W1 = "2024-06-03T09:00:00Z"   # max updated_at of the good records in orders_v1.json
W2 = "2024-06-04T11:00:00Z"   # ... in orders_v2.json (112 is bad, so its 12:00 does not count)


def records(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def key(email):
    return hmac.new(SECRET, email.encode(), hashlib.sha256).hexdigest()[:16]


def parse(ts):
    return datetime.fromisoformat(ts).astimezone(timezone.utc)


class SimulatedCrash(Exception):
    """Stands for the process being killed at this exact point."""


class FakeAPI:
    """The Pagebound Orders API with cursor pagination and updated_since (>=)."""

    def __init__(self, data):
        self.data = data
        self.requests = []          # the query parameters of every request, in order
        self.failures = {}          # request number (1-based) -> status, (status, headers) or exception class
        self.down_cursors = set()   # requests with one of these cursors always fail with ConnectError

    def handler(self, request):
        params = dict(request.url.params)
        self.requests.append(params)
        number = len(self.requests)
        assert request.method == "GET" and request.url.path == "/v1/orders", (
            f"Unexpected request {request.method} {request.url.path}; use GET /v1/orders."
        )
        if params.get("cursor") in self.down_cursors:
            raise httpx.ConnectError("simulated: connection refused", request=request)
        failure = self.failures.get(number)
        if isinstance(failure, type) and issubclass(failure, Exception):
            raise failure("simulated network problem", request=request)
        if isinstance(failure, int):
            return httpx.Response(failure, json={"error": "simulated"})
        if isinstance(failure, tuple):
            status, headers = failure
            return httpx.Response(status, headers=headers, json={"error": "simulated"})

        rows = list(self.data)
        if "updated_since" in params:
            since = parse(params["updated_since"])
            rows = [r for r in rows if parse(r["updated_at"]) >= since]
        rows.sort(key=lambda r: (parse(r["updated_at"]), r["id"]))
        offset = int(params["cursor"][1:]) if "cursor" in params else 0
        limit = int(params["limit"])
        page = rows[offset:offset + limit]
        nxt = offset + limit
        return httpx.Response(200, json={"items": page, "next_cursor": f"c{nxt}" if nxt < len(rows) else None})

    def client(self):
        return httpx.Client(transport=httpx.MockTransport(self.handler), base_url=BASE)


class FakeSleep:
    def __init__(self):
        self.delays = []

    def __call__(self, seconds):
        self.delays.append(seconds)


def run(api, out, run_id="r1", sleep=None, **kwargs):
    sleep = sleep if sleep is not None else FakeSleep()
    with api.client() as client:
        return run_pipeline(client, out, SECRET, run_id, sleep=sleep, **kwargs)


def db_rows(out, sql):
    conn = sqlite3.connect(out / "warehouse.db")
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def orders(out):
    return db_rows(out, "SELECT id, customer_key, city, status, amount_cents, currency, created_at, "
                        "updated_at, item_qty FROM orders ORDER BY id")


def quarantined(out):
    return db_rows(out, "SELECT record_id, field FROM quarantine ORDER BY record_id")


def watermark(out):
    found = db_rows(out, "SELECT value FROM state WHERE key = 'orders_watermark'")
    return found[0][0] if found else None


def partitions(out):
    """{folder name: sorted ids} for every partition folder, reading each folder's files."""
    root = out / "parquet"
    if not root.exists():
        return {}
    result = {}
    for folder in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))):
        result[folder.name] = sorted(pq.read_table(folder).column("id").to_pylist())
    return result


def snapshot(out):
    return orders(out), quarantined(out), watermark(out), partitions(out)


EXPECTED_V1 = [
    (101, key("asha@example.com"), "Pune", "shipped", 1999, "INR", "2024-06-01T10:00:00Z", "2024-06-01T12:00:00Z", 2),
    (102, key("ravi@example.com"), None, "pending", 25000, "INR", "2024-06-01T11:00:00Z", "2024-06-01T12:30:00Z", 2),
    (104, key("meera@example.com"), "Delhi", "cancelled", 0, "INR", "2024-06-01T20:00:00Z", "2024-06-02T08:00:00Z", 0),
    (105, key("asha@example.com"), "Pune", "shipped", 550, "INR", "2024-06-02T09:00:00Z", "2024-06-02T09:15:00Z", 1),
    (108, key("kiran@example.com"), "Mumbai", "shipped", 120000, "INR", "2024-06-03T07:00:00Z", "2024-06-03T07:30:00Z", 3),
    (109, key("dev@example.com"), "Pune", "pending", 7525, "INR", "2024-06-03T08:00:00Z", "2024-06-03T09:00:00Z", 1),
    (110, key("ravi@example.com"), None, "shipped", 1000, "INR", "2024-06-03T08:30:00Z", "2024-06-03T09:00:00Z", 4),
]
EXPECTED_PARTS_V1 = {
    "order_date=2024-06-01": [101, 102, 104],
    "order_date=2024-06-02": [105],
    "order_date=2024-06-03": [108, 109, 110],
}
EXPECTED_QUARANTINE_V1 = [("103", "amount"), ("106", "status"), ("107", "email")]


# =============================================================== unit checks

def test_transform_clean_record():
    rec = records("orders_v1.json")[3]   # order 104, created with a +05:30 offset
    row = transform(rec, SECRET)
    assert row == {
        "id": 104, "customer_key": key("meera@example.com"), "city": "Delhi", "status": "cancelled",
        "amount_cents": 0, "currency": "INR", "created_at": "2024-06-01T20:00:00Z",
        "updated_at": "2024-06-02T08:00:00Z", "item_qty": 0,
    }, (
        f"transform(order 104) gave {row}. created_at 2024-06-02T01:30:00+05:30 is 2024-06-01T20:00:00Z; "
        "an empty items list has item_qty 0; the email becomes customer_key and is not kept."
    )


def test_transform_normalises_and_converts():
    by_id = {r["id"]: r for r in records("orders_v1.json")}
    assert transform(by_id[105], SECRET)["amount_cents"] == 550, "'5.5' is 550 cents (use Decimal, never float)."
    row = transform(by_id[108], SECRET)
    assert row["customer_key"] == key("kiran@example.com"), (
        "'  Kiran@Example.COM ' must be stripped and lower-cased before the HMAC, so it matches kiran@example.com."
    )
    assert row["amount_cents"] == 120000 and row["item_qty"] == 3


@pytest.mark.parametrize("change, field", [
    ({"amount": "12,50"}, "amount"),
    ({"amount": "-3.00"}, "amount"),
    ({"amount": "19.999"}, "amount"),
    ({"amount": "NaN"}, "amount"),
    ({"amount": 19.99}, "amount"),
    ({"status": "lost"}, "status"),
    ({"customer": {"city": "Goa"}}, "email"),
    ({"customer": {"email": "not-an-email", "city": "Goa"}}, "email"),
    ({"id": "101"}, "id"),
    ({"id": True}, "id"),
    ({"currency": "rupees"}, "currency"),
    ({"created_at": "2024-06-01T10:00:00"}, "created_at"),
    ({"updated_at": "yesterday"}, "updated_at"),
    ({"items": [{"sku": "B1", "qty": 0}]}, "items"),
])
def test_transform_rejects_bad_records(change, field):
    rec = {**records("orders_v1.json")[0], **change}
    with pytest.raises(BadRecord) as info:
        transform(rec, SECRET)
    assert info.value.field == field, (
        f"{change} must be rejected with BadRecord field {field!r}, got {info.value.field!r}."
    )
    assert isinstance(info.value, ValueError), "BadRecord should subclass ValueError."


def test_checkpoint_helpers(tmp_path):
    path = tmp_path / "checkpoint.json"
    assert load_checkpoint(path) is None, "A missing checkpoint means 'start fresh': return None."
    state = {"run_id": "r1", "since": None, "cursor": "c3", "max_updated_at": "2024-06-01T12:30:00Z",
             "days": ["2024-06-01"], "fetch_done": False}
    save_checkpoint(path, state)
    save_checkpoint(path, {**state, "cursor": "c6"})
    assert load_checkpoint(path)["cursor"] == "c6", "save_checkpoint must replace the previous checkpoint."
    assert sorted(p.name for p in tmp_path.iterdir()) == ["checkpoint.json"], (
        "A temporary file was left behind. Write to a temp file in the same folder, then os.replace it."
    )
    path.write_text('{"cursor": "c', encoding="utf-8")
    with pytest.raises(ValueError):
        load_checkpoint(path)


def test_load_secret():
    assert load_secret({"PAGEBOUND_PSEUDO_KEY": " abc-0123456789-xyz "}) == b"abc-0123456789-xyz"
    with pytest.raises(RuntimeError) as info:
        load_secret({})
    assert "PAGEBOUND_PSEUDO_KEY" in str(info.value), "Name the missing variable in the error."


# =============================================================== first run

def test_first_run_loads_good_records_and_reports(tmp_path):
    api = FakeAPI(records("orders_v1.json"))
    summary = run(api, tmp_path / "out")
    assert orders(tmp_path / "out") == EXPECTED_V1, (
        "The orders table is wrong after the first run. Expected the 7 good orders, emails replaced by "
        "customer_key, amounts in cents, timestamps as UTC 'YYYY-MM-DDTHH:MM:SSZ'."
    )
    expected = {"run_id": "r1", "resumed": False, "pages": 4, "fetched": 10, "loaded": 7, "inserted": 7,
                "updated": 0, "unchanged": 0, "quarantined": 3,
                "partitions": ["2024-06-01", "2024-06-02", "2024-06-03"], "watermark": W1}
    got = {k: summary.get(k) for k in expected}
    assert got == expected, f"Run summary is {got}, expected {expected}."


def test_first_run_requests(tmp_path):
    api = FakeAPI(records("orders_v1.json"))
    run(api, tmp_path / "out")
    assert api.requests == [{"limit": "3"}, {"limit": "3", "cursor": "c3"},
                            {"limit": "3", "cursor": "c6"}, {"limit": "3", "cursor": "c9"}], (
        f"Requests were {api.requests}. The first run has no watermark, so no updated_since; follow "
        "next_cursor until it is null; send limit every time."
    )


def test_bad_records_are_quarantined_not_fatal(tmp_path):
    out = tmp_path / "out"
    run(FakeAPI(records("orders_v1.json")), out)
    assert quarantined(out) == EXPECTED_QUARANTINE_V1, (
        f"Quarantine holds {quarantined(out)}. 103 has amount '12,50', 106 status 'lost', 107 no email. "
        "record_id is json.dumps of the id; field is BadRecord.field."
    )
    reasons = db_rows(out, "SELECT reason, run_id FROM quarantine")
    assert all(reason and run_id == "r1" for reason, run_id in reasons), "Store a reason and the run_id."


def test_watermark_and_checkpoint_after_success(tmp_path):
    out = tmp_path / "out"
    run(FakeAPI(records("orders_v1.json")), out)
    assert watermark(out) == W1, (
        f"Watermark is {watermark(out)!r}, expected {W1!r}: the largest updated_at of the loaded records."
    )
    assert not (out / "checkpoint.json").exists(), "Delete the checkpoint when the run finished successfully."


def test_parquet_partitions(tmp_path):
    out = tmp_path / "out"
    run(FakeAPI(records("orders_v1.json")), out)
    assert partitions(out) == EXPECTED_PARTS_V1, (
        f"Parquet partitions are {partitions(out)}. One folder per UTC created day "
        "(order 104 belongs to 2024-06-01)."
    )
    for name in EXPECTED_PARTS_V1:
        files = sorted(p.name for p in (out / "parquet" / name).iterdir())
        assert files == ["part-0.parquet"], f"{name} contains {files}; write exactly part-0.parquet."


def test_parquet_schema_and_values(tmp_path):
    out = tmp_path / "out"
    run(FakeAPI(records("orders_v1.json")), out)
    table = pq.read_table(out / "parquet" / "order_date=2024-06-01" / "part-0.parquet")
    expected_types = {
        "id": pa.int64(), "customer_key": pa.string(), "city": pa.string(), "status": pa.string(),
        "amount": pa.decimal128(12, 2), "currency": pa.string(),
        "created_at": pa.timestamp("us", tz="UTC"), "updated_at": pa.timestamp("us", tz="UTC"),
        "item_qty": pa.int64(),
    }
    got_types = {f.name: f.type for f in table.schema}
    assert got_types == expected_types, f"Parquet schema is {got_types}."
    first = table.to_pylist()[0]
    assert first["amount"] == Decimal("19.99") and type(first["amount"]) is Decimal, "amount is a Decimal 19.99."
    assert first["created_at"] == datetime(2024, 6, 1, 10, 0, tzinfo=timezone.utc)
    assert first["customer_key"] == key("asha@example.com")


def test_no_emails_anywhere(tmp_path):
    out = tmp_path / "out"
    run(FakeAPI(records("orders_v1.json")), out)
    cols = [r[1] for r in db_rows(out, "PRAGMA table_info(orders)")]
    assert "email" not in cols, "The orders table must not have an email column."
    raw_db = (out / "warehouse.db").read_bytes()
    assert b"example.com" not in raw_db.lower(), (
        "An email address is stored in warehouse.db (orders or quarantine). Store only the pseudonym; "
        "the quarantine table keeps id, field and reason, not the raw record."
    )
    for file in (out / "parquet").rglob("*.parquet"):
        assert b"example.com" not in file.read_bytes().lower(), f"An email is stored in {file.name}."


# =============================================================== re-runs

def test_rerun_without_changes_changes_nothing(tmp_path):
    out = tmp_path / "out"
    run(FakeAPI(records("orders_v1.json")), out)
    before = snapshot(out)
    api = FakeAPI(records("orders_v1.json"))
    summary = run(api, out, run_id="r2")
    assert api.requests == [{"limit": "3", "updated_since": W1}], (
        f"Second run requests: {api.requests}. Start from the stored watermark with updated_since; "
        "the API uses >=, so only 109 and 110 come back, in one page."
    )
    assert snapshot(out) == before, "Running again with no new data must leave every table and file the same."
    got = {k: summary[k] for k in ("loaded", "inserted", "updated", "unchanged", "quarantined", "partitions")}
    assert got == {"loaded": 2, "inserted": 0, "updated": 0, "unchanged": 2, "quarantined": 0,
                   "partitions": ["2024-06-03"]}, (
        f"Second run summary {got}. 109 and 110 are re-fetched (>=) but not newer: unchanged."
    )


def test_second_run_with_new_and_updated_orders(tmp_path):
    out = tmp_path / "out"
    run(FakeAPI(records("orders_v1.json")), out)
    api = FakeAPI(records("orders_v2.json"))
    summary = run(api, out, run_id="r2")
    assert api.requests == [{"limit": "3", "updated_since": W1},
                            {"limit": "3", "updated_since": W1, "cursor": "c3"}], f"Requests: {api.requests}"
    got = {k: summary[k] for k in ("fetched", "loaded", "inserted", "updated", "unchanged", "quarantined",
                                   "partitions", "watermark")}
    assert got == {"fetched": 6, "loaded": 5, "inserted": 2, "updated": 1, "unchanged": 2, "quarantined": 1,
                   "partitions": ["2024-06-01", "2024-06-03", "2024-06-04"], "watermark": W2}, (
        f"Summary {got}. Fetched since {W1}: 109, 110 (unchanged), 111 (new), 102 (updated), 113 (new, "
        "but created on 1 June), 112 (bad amount)."
    )
    rows = {r[0]: r for r in orders(out)}
    assert sorted(rows) == [101, 102, 104, 105, 108, 109, 110, 111, 113]
    assert rows[102][3] == "shipped" and rows[102][7] == "2024-06-04T10:00:00Z", (
        "Order 102 has a newer updated_at, so its row must be updated."
    )
    assert watermark(out) == W2, (
        f"Watermark {watermark(out)!r}. 112 is quarantined, so the watermark is 113's {W2}."
    )
    assert partitions(out) == {
        "order_date=2024-06-01": [101, 102, 104, 113],
        "order_date=2024-06-02": [105],
        "order_date=2024-06-03": [108, 109, 110],
        "order_date=2024-06-04": [111],
    }, (
        f"Partitions {partitions(out)}. Rewrite every day touched by a loaded record from the full "
        "SQLite table: 2024-06-01 now also holds the late order 113 and the updated 102."
    )
    assert quarantined(out) == EXPECTED_QUARANTINE_V1 + [("112", "amount")]


def test_quarantine_is_idempotent(tmp_path):
    out = tmp_path / "out"
    run(FakeAPI(records("orders_v1.json")), out)
    run(FakeAPI(records("orders_v2.json")), out, run_id="r2")
    api = FakeAPI(records("orders_v2.json"))
    summary = run(api, out, run_id="r3")
    assert api.requests == [{"limit": "3", "updated_since": W2}]
    assert summary["quarantined"] == 1 and summary["unchanged"] == 1, (
        "Run 3 re-fetches 113 (unchanged) and the bad 112 again."
    )
    assert quarantined(out) == EXPECTED_QUARANTINE_V1 + [("112", "amount")], (
        f"Quarantine holds {quarantined(out)}. The same bad record seen again must not add a second "
        "row: key the quarantine on (record_id, updated_at) and INSERT OR IGNORE."
    )


def test_running_the_same_input_twice_is_identical(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    run(FakeAPI(records("orders_v1.json")), a)
    run(FakeAPI(records("orders_v1.json")), b)
    run(FakeAPI(records("orders_v1.json")), b, run_id="r2")
    run(FakeAPI(records("orders_v1.json")), b, run_id="r3")
    assert snapshot(b) == snapshot(a), "Three runs over the same data must give the same result as one."


def test_limit_parameter_is_used(tmp_path):
    out = tmp_path / "out"
    api = FakeAPI(records("orders_v1.json"))
    summary = run(api, out, limit=4)
    assert [r.get("cursor") for r in api.requests] == [None, "c4", "c8"] and summary["pages"] == 3
    assert orders(out) == EXPECTED_V1


def test_empty_api(tmp_path):
    out = tmp_path / "out"
    api = FakeAPI([])
    summary = run(api, out)
    assert len(api.requests) == 1 and summary["pages"] == 1
    assert summary["watermark"] is None and watermark(out) is None, "No records: no watermark yet."
    assert summary["partitions"] == [] and orders(out) == []
    assert not (out / "checkpoint.json").exists()


# =============================================================== retries

def test_429_honours_retry_after(tmp_path):
    out = tmp_path / "out"
    api = FakeAPI(records("orders_v1.json"))
    api.failures = {1: (429, {"Retry-After": "2"})}
    sleep = FakeSleep()
    run(api, out, sleep=sleep)
    assert sleep.delays == [2.0], f"Slept {sleep.delays}. On 429 with Retry-After: 2, wait 2 seconds."
    assert len(api.requests) == 5 and orders(out) == EXPECTED_V1


def test_5xx_exponential_backoff(tmp_path):
    out = tmp_path / "out"
    api = FakeAPI(records("orders_v1.json"))
    api.failures = {2: 503, 3: 502}
    sleep = FakeSleep()
    run(api, out, sleep=sleep, base_delay=0.5)
    assert sleep.delays == [0.5, 1.0], f"Slept {sleep.delays}; backoff is base_delay * 2**(attempt-1)."
    assert len(api.requests) == 6 and orders(out) == EXPECTED_V1


def test_404_is_not_retried(tmp_path):
    out = tmp_path / "out"
    api = FakeAPI(records("orders_v1.json"))
    api.failures = {1: 404}
    sleep = FakeSleep()
    with pytest.raises(httpx.HTTPStatusError):
        run(api, out, sleep=sleep)
    assert len(api.requests) == 1 and sleep.delays == [], "4xx (except 429) is permanent: no retry, no sleep."


def test_missing_secret_stops_before_any_request(tmp_path):
    api = FakeAPI(records("orders_v1.json"))
    with api.client() as client:
        with pytest.raises(ValueError):
            run_pipeline(client, tmp_path / "out", b"", "r1", sleep=FakeSleep())
    assert api.requests == [], "Check the secret before fetching anything."


def test_endless_api_is_stopped(tmp_path):
    calls = []

    def endless(request):
        calls.append(dict(request.url.params))
        if len(calls) > 50:
            raise AssertionError(
                "50 requests to an API whose next_cursor never ends: the max_pages guard is missing. "
                "Count the pages of this run and raise RuntimeError once max_pages pages were fetched."
            )
        return httpx.Response(200, json={"items": [], "next_cursor": f"again{len(calls)}"})

    with httpx.Client(transport=httpx.MockTransport(endless), base_url=BASE) as client:
        with pytest.raises(RuntimeError):
            run_pipeline(client, tmp_path / "out", SECRET, "r1", sleep=FakeSleep(), max_pages=5)
    assert len(calls) == 5, f"{len(calls)} requests were made; stop after max_pages=5 pages."


# =============================================================== crashes and resume

def test_crash_while_fetching_then_resume(tmp_path):
    out = tmp_path / "out"
    clean = tmp_path / "clean"
    run(FakeAPI(records("orders_v1.json")), clean)

    api = FakeAPI(records("orders_v1.json"))
    api.down_cursors = {"c3"}
    sleep = FakeSleep()
    with pytest.raises(httpx.ConnectError):
        run(api, out, sleep=sleep, max_attempts=4)
    assert len(api.requests) == 5 and sleep.delays == [0.5, 1.0, 2.0], (
        f"{len(api.requests)} requests, sleeps {sleep.delays}: page 1 once, then page 2 four times "
        "(max_attempts=4) with three backoff sleeps, then give up by raising the error."
    )
    assert [r[0] for r in orders(out)] == [101, 102], "Page 1 must be committed before page 2 is fetched."
    assert watermark(out) is None, "The watermark moves only at the end of a successful run."
    state = json.loads((out / "checkpoint.json").read_text(encoding="utf-8"))
    got = {k: state.get(k) for k in ("since", "cursor", "max_updated_at", "days", "fetch_done")}
    assert got == {"since": None, "cursor": "c3", "max_updated_at": "2024-06-01T12:30:00Z",
                   "days": ["2024-06-01"], "fetch_done": False}, f"Checkpoint after the crash: {got}"

    api2 = FakeAPI(records("orders_v1.json"))
    summary = run(api2, out, run_id="r2")
    assert api2.requests == [{"limit": "3", "cursor": "c3"}, {"limit": "3", "cursor": "c6"},
                             {"limit": "3", "cursor": "c9"}], (
        f"Resume requests: {api2.requests}. Continue from the checkpoint's cursor (and its since), "
        "do not start again from page 1."
    )
    assert summary["resumed"] is True and summary["inserted"] == 5 and summary["quarantined"] == 2
    assert snapshot(out) == snapshot(clean), "After resuming, the result must equal a run that never crashed."
    assert not (out / "checkpoint.json").exists()


def test_crash_after_commit_before_checkpoint(tmp_path, monkeypatch):
    out = tmp_path / "out"
    clean = tmp_path / "clean"
    run(FakeAPI(records("orders_v1.json")), clean)

    real_save = solution.save_checkpoint

    def crash_after_page_2(path, state):
        if state.get("cursor") == "c6":
            raise SimulatedCrash("killed after page 2 was committed")
        real_save(path, state)

    monkeypatch.setattr(solution, "save_checkpoint", crash_after_page_2)
    with pytest.raises(SimulatedCrash):
        run(FakeAPI(records("orders_v1.json")), out)
    assert [r[0] for r in orders(out)] == [101, 102, 104, 105], (
        f"SQLite holds {[r[0] for r in orders(out)]} when the checkpoint after page 2 is being saved. "
        "Commit a page's data FIRST, then save the checkpoint that points past it. The other order "
        "loses the page for good: the checkpoint says 'page 2 done', so the resume skips it."
    )
    monkeypatch.setattr(solution, "save_checkpoint", real_save)

    api = FakeAPI(records("orders_v1.json"))
    summary = run(api, out, run_id="r2")
    assert [r.get("cursor") for r in api.requests] == ["c3", "c6", "c9"], (
        "The checkpoint still points at page 2, so page 2 is fetched again."
    )
    assert summary["inserted"] == 3 and summary["unchanged"] == 2, (
        f"Resume summary {summary}. Page 2's orders are already in SQLite: the upsert must see them "
        "as unchanged, not insert them twice."
    )
    assert snapshot(out) == snapshot(clean), (
        "Repeating a page after a crash must not duplicate anything (orders, quarantine, partitions). "
        "Partitions come from every loaded record, so 2024-06-02 is still exported."
    )


def test_crash_during_export_then_resume(tmp_path, monkeypatch):
    out = tmp_path / "out"
    clean = tmp_path / "clean"
    run(FakeAPI(records("orders_v1.json")), clean)

    real_export = solution.export_partition

    def crash_on_june_2(conn, parquet_root, day):
        if day == "2024-06-02":
            raise SimulatedCrash("disk full")
        return real_export(conn, parquet_root, day)

    monkeypatch.setattr(solution, "export_partition", crash_on_june_2)
    with pytest.raises(SimulatedCrash):
        run(FakeAPI(records("orders_v1.json")), out)
    assert watermark(out) is None, (
        "The export failed, so the run is not finished: do not commit the watermark yet."
    )
    state = json.loads((out / "checkpoint.json").read_text(encoding="utf-8"))
    assert state["fetch_done"] is True and state["days"] == ["2024-06-01", "2024-06-02", "2024-06-03"], (
        f"Checkpoint {state}. After the last page the checkpoint must say fetching is done and list every day."
    )
    monkeypatch.setattr(solution, "export_partition", real_export)

    api = FakeAPI(records("orders_v1.json"))
    summary = run(api, out, run_id="r2")
    assert api.requests == [], (
        f"The resume made {len(api.requests)} requests. All pages were already loaded; only the export "
        "and the watermark were missing."
    )
    assert summary["pages"] == 0 and summary["partitions"] == ["2024-06-01", "2024-06-02", "2024-06-03"]
    assert snapshot(out) == snapshot(clean)


# =============================================================== logging

def test_logging(tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    run(FakeAPI(records("orders_v1.json")), tmp_path / "out", run_id="r-log-1")
    messages = [r.getMessage() for r in caplog.records]
    pipeline = [r for r in caplog.records if r.name == "pagebound.pipeline"]
    warnings = [r.getMessage() for r in pipeline if r.levelno == logging.WARNING]
    for order_id, field in [("103", "amount"), ("106", "status"), ("107", "email")]:
        assert any(order_id in m and field in m for m in warnings), (
            f"No WARNING from 'pagebound.pipeline' names order {order_id} and the field {field!r}. "
            f"Warnings were: {warnings}"
        )
    summaries = [r.getMessage() for r in pipeline if r.levelno == logging.INFO and "run_id=r-log-1" in r.getMessage()]
    assert any("loaded=7" in m and "quarantined=3" in m for m in summaries), (
        f"No INFO summary line with run_id=r-log-1, loaded=7 and quarantined=3. Lines: {summaries}"
    )
    for m in messages:
        assert "@" not in m and "example.com" not in m.lower(), f"A log line contains an email: {m!r}"
        assert SECRET.decode() not in m, f"A log line contains the secret: {m!r}"
