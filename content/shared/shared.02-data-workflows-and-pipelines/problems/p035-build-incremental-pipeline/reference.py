"""Pagebound orders pipeline: API -> SQLite (upsert) + partitioned Parquet.

Incremental (watermark), resumable (checkpoint), re-run safe (upserts, partition overwrite,
idempotent quarantine), with retries, pseudonymised emails and a logged run summary.
"""

import hashlib
import hmac
import json
import logging
import os
import sqlite3
import time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import httpx
import pyarrow as pa
import pyarrow.parquet as pq

log = logging.getLogger("pagebound.pipeline")

ENV_VAR = "PAGEBOUND_PSEUDO_KEY"
STATUSES = {"shipped", "pending", "cancelled"}
WATERMARK_KEY = "orders_watermark"

PARQUET_SCHEMA = pa.schema([
    pa.field("id", pa.int64(), nullable=False),
    pa.field("customer_key", pa.string()),
    pa.field("city", pa.string()),
    pa.field("status", pa.string(), nullable=False),
    pa.field("amount", pa.decimal128(12, 2), nullable=False),
    pa.field("currency", pa.string(), nullable=False),
    pa.field("created_at", pa.timestamp("us", tz="UTC"), nullable=False),
    pa.field("updated_at", pa.timestamp("us", tz="UTC"), nullable=False),
    pa.field("item_qty", pa.int64(), nullable=False),
])

DDL = """
CREATE TABLE IF NOT EXISTS orders (
    id           INTEGER PRIMARY KEY,
    customer_key TEXT NOT NULL,
    city         TEXT,
    status       TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    currency     TEXT NOT NULL,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL,
    item_qty     INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS quarantine (
    record_id  TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    field      TEXT NOT NULL,
    reason     TEXT NOT NULL,
    run_id     TEXT NOT NULL,
    PRIMARY KEY (record_id, updated_at)
);
CREATE TABLE IF NOT EXISTS state (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

ORDER_COLUMNS = ["id", "customer_key", "city", "status", "amount_cents", "currency",
                 "created_at", "updated_at", "item_qty"]


# ---------------------------------------------------------------- secrets and PII

def load_secret(env=None):
    if env is None:
        env = os.environ
    value = env.get(ENV_VAR, "").strip()
    if not value:
        raise RuntimeError(f"{ENV_VAR} is not set")
    return value.encode("utf-8")


def pseudonymise(email, secret):
    normalised = email.strip().lower()
    return hmac.new(secret, normalised.encode("utf-8"), hashlib.sha256).hexdigest()[:16]


# ---------------------------------------------------------------- transform + validation

class BadRecord(ValueError):
    def __init__(self, field, message):
        super().__init__(f"{field}: {message}")
        self.field = field


def utc_text(value, field):
    if not isinstance(value, str):
        raise BadRecord(field, "missing or not a string")
    try:
        moment = datetime.fromisoformat(value)
    except ValueError:
        raise BadRecord(field, "not an ISO timestamp") from None
    if moment.tzinfo is None:
        raise BadRecord(field, "timestamp has no time zone")
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def transform(record, secret):
    """Validate one API record and return the clean row, or raise BadRecord(field, ...)."""
    if not isinstance(record, dict):
        raise BadRecord("record", "not a JSON object")

    order_id = record.get("id")
    if type(order_id) is not int or order_id <= 0:
        raise BadRecord("id", "must be a positive integer")

    customer = record.get("customer")
    if not isinstance(customer, dict):
        raise BadRecord("email", "customer is missing")
    email = customer.get("email")
    if not isinstance(email, str):
        raise BadRecord("email", "missing")
    local, at, domain = email.strip().rpartition("@")
    if not at or not local or not domain:
        raise BadRecord("email", "not an email address")

    city = customer.get("city")
    if city is not None and not isinstance(city, str):
        raise BadRecord("city", "must be text or null")
    if city is not None:
        city = city.strip() or None

    status = record.get("status")
    if status not in STATUSES:
        raise BadRecord("status", "unknown status")

    raw_amount = record.get("amount")
    if not isinstance(raw_amount, str):
        raise BadRecord("amount", "must be a decimal string")
    try:
        amount = Decimal(raw_amount)
    except InvalidOperation:
        raise BadRecord("amount", "not a decimal number") from None
    if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
        raise BadRecord("amount", "must be >= 0 with at most 2 decimal places")

    currency = record.get("currency")
    if not (isinstance(currency, str) and len(currency) == 3 and currency.isalpha() and currency.isupper()):
        raise BadRecord("currency", "must be a 3-letter code")

    created_at = utc_text(record.get("created_at"), "created_at")
    updated_at = utc_text(record.get("updated_at"), "updated_at")

    items = record.get("items")
    if not isinstance(items, list):
        raise BadRecord("items", "must be a list")
    qty = 0
    for item in items:
        n = item.get("qty") if isinstance(item, dict) else None
        if type(n) is not int or n < 1:
            raise BadRecord("items", "every item needs a qty >= 1")
        qty += n

    return {
        "id": order_id,
        "customer_key": pseudonymise(email, secret),
        "city": city,
        "status": status,
        "amount_cents": int(amount * 100),
        "currency": currency,
        "created_at": created_at,
        "updated_at": updated_at,
        "item_qty": qty,
    }


# ---------------------------------------------------------------- checkpoint

def save_checkpoint(path, state):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(state, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def load_checkpoint(path):
    path = Path(path)
    if not path.exists():
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"checkpoint {path.name} is corrupt: {error}") from None
    if not isinstance(state, dict):
        raise ValueError(f"checkpoint {path.name} is not a JSON object")
    return state


# ---------------------------------------------------------------- extract with retries

def fetch_page(client, params, *, max_attempts, base_delay, sleep):
    for attempt in range(1, max_attempts + 1):
        last = attempt == max_attempts
        try:
            response = client.get("/v1/orders", params=params)
        except httpx.TransportError as error:
            if last:
                raise
            delay = base_delay * 2 ** (attempt - 1)
            log.warning("attempt %d failed (%s); retrying in %.1fs", attempt, type(error).__name__, delay)
            sleep(delay)
            continue
        status = response.status_code
        if status == 429 or status >= 500:
            if last:
                response.raise_for_status()
            delay = base_delay * 2 ** (attempt - 1)
            retry_after = response.headers.get("Retry-After")
            if retry_after is not None:
                try:
                    delay = float(retry_after)
                except ValueError:
                    pass
            log.warning("attempt %d got HTTP %d; retrying in %.1fs", attempt, status, delay)
            sleep(delay)
            continue
        response.raise_for_status()
        body = response.json()
        if not isinstance(body, dict) or not isinstance(body.get("items"), list):
            raise ValueError("unexpected response shape: no 'items' list")
        return body
    raise AssertionError("unreachable")


# ---------------------------------------------------------------- load

def upsert(conn, row):
    """Insert or update-if-newer. Returns 'inserted', 'updated' or 'unchanged'."""
    found = conn.execute("SELECT updated_at FROM orders WHERE id = ?", (row["id"],)).fetchone()
    if found is not None and found[0] >= row["updated_at"]:
        return "unchanged"
    names = ", ".join(ORDER_COLUMNS)
    marks = ", ".join("?" for _ in ORDER_COLUMNS)
    updates = ", ".join(f"{c} = excluded.{c}" for c in ORDER_COLUMNS if c != "id")
    conn.execute(
        f"INSERT INTO orders ({names}) VALUES ({marks}) "
        f"ON CONFLICT(id) DO UPDATE SET {updates} WHERE excluded.updated_at > orders.updated_at",
        [row[c] for c in ORDER_COLUMNS],
    )
    return "inserted" if found is None else "updated"


def quarantine(conn, record, error, run_id):
    record_id = json.dumps(record.get("id")) if isinstance(record, dict) else "null"
    updated_at = str(record.get("updated_at")) if isinstance(record, dict) else "None"
    conn.execute(
        "INSERT OR IGNORE INTO quarantine (record_id, updated_at, field, reason, run_id) VALUES (?, ?, ?, ?, ?)",
        (record_id, updated_at, error.field, str(error), run_id),
    )
    log.warning("quarantined order %s: %s", record_id, error)


# ---------------------------------------------------------------- export

def export_partition(conn, parquet_root, day):
    rows = conn.execute(
        f"SELECT {', '.join(ORDER_COLUMNS)} FROM orders WHERE substr(created_at, 1, 10) = ? ORDER BY id",
        (day,),
    ).fetchall()
    records = []
    for values in rows:
        row = dict(zip(ORDER_COLUMNS, values))
        records.append({
            "id": row["id"],
            "customer_key": row["customer_key"],
            "city": row["city"],
            "status": row["status"],
            "amount": Decimal(row["amount_cents"]) / 100,
            "currency": row["currency"],
            "created_at": datetime.fromisoformat(row["created_at"]),
            "updated_at": datetime.fromisoformat(row["updated_at"]),
            "item_qty": row["item_qty"],
        })
    table = pa.Table.from_pylist(records, schema=PARQUET_SCHEMA)
    folder = Path(parquet_root) / f"order_date={day}"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "part-0.parquet"
    tmp = folder / ".part-0.parquet.tmp"
    pq.write_table(table, tmp)
    os.replace(tmp, target)
    return target


# ---------------------------------------------------------------- the run

def run_pipeline(client, out_dir, secret, run_id, *, limit=3, max_pages=100, max_attempts=4,
                 base_delay=0.5, sleep=time.sleep):
    if not secret:
        raise ValueError("a pseudonymisation secret is required")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ckpt_path = out_dir / "checkpoint.json"
    parquet_root = out_dir / "parquet"

    started = time.monotonic()
    summary = {"run_id": run_id, "resumed": False, "pages": 0, "fetched": 0, "loaded": 0,
               "inserted": 0, "updated": 0, "unchanged": 0, "quarantined": 0,
               "partitions": [], "watermark": None}

    conn = sqlite3.connect(out_dir / "warehouse.db")
    try:
        conn.executescript(DDL)
        found = conn.execute("SELECT value FROM state WHERE key = ?", (WATERMARK_KEY,)).fetchone()
        committed = found[0] if found else None

        state = load_checkpoint(ckpt_path)
        if state is not None:
            summary["resumed"] = True
            log.info("run %s resuming from checkpoint of run %s", run_id, state.get("run_id"))
        else:
            state = {"run_id": run_id, "since": committed, "cursor": None,
                     "max_updated_at": None, "days": [], "fetch_done": False}
        days = set(state["days"])

        while not state["fetch_done"]:
            if summary["pages"] >= max_pages:
                raise RuntimeError(f"more than max_pages={max_pages} pages; is the API looping?")
            params = {"limit": limit}
            if state["since"] is not None:
                params["updated_since"] = state["since"]
            if state["cursor"] is not None:
                params["cursor"] = state["cursor"]
            page = fetch_page(client, params, max_attempts=max_attempts,
                              base_delay=base_delay, sleep=sleep)
            summary["pages"] += 1

            max_seen = state["max_updated_at"]
            with conn:  # one transaction per page: the page is loaded completely or not at all
                for record in page["items"]:
                    summary["fetched"] += 1
                    try:
                        row = transform(record, secret)
                    except BadRecord as error:
                        quarantine(conn, record, error, run_id)
                        summary["quarantined"] += 1
                        continue
                    summary[upsert(conn, row)] += 1
                    summary["loaded"] += 1
                    days.add(row["created_at"][:10])
                    if max_seen is None or row["updated_at"] > max_seen:
                        max_seen = row["updated_at"]

            # Data first, checkpoint second: a crash in between only repeats this page.
            next_cursor = page.get("next_cursor")
            state = {**state, "cursor": next_cursor, "max_updated_at": max_seen,
                     "days": sorted(days), "fetch_done": next_cursor is None}
            save_checkpoint(ckpt_path, state)
            log.info("run %s page %d: %d records", run_id, summary["pages"], len(page["items"]))

        for day in sorted(days):
            export_partition(conn, parquet_root, day)
        summary["partitions"] = sorted(days)

        new_mark = committed
        if state["max_updated_at"] is not None and (new_mark is None or state["max_updated_at"] > new_mark):
            new_mark = state["max_updated_at"]
        if new_mark is not None:
            with conn:
                conn.execute(
                    "INSERT INTO state (key, value) VALUES (?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                    (WATERMARK_KEY, new_mark),
                )
        summary["watermark"] = new_mark
        ckpt_path.unlink(missing_ok=True)
    finally:
        conn.close()

    log.info(
        "run_id=%s done: resumed=%s pages=%d fetched=%d loaded=%d inserted=%d updated=%d "
        "unchanged=%d quarantined=%d partitions=%d watermark=%s seconds=%.2f",
        run_id, summary["resumed"], summary["pages"], summary["fetched"], summary["loaded"],
        summary["inserted"], summary["updated"], summary["unchanged"], summary["quarantined"],
        len(summary["partitions"]), summary["watermark"], time.monotonic() - started,
    )
    return summary


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    secret = load_secret()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    with httpx.Client(base_url=os.environ.get("PAGEBOUND_BASE_URL", "https://api.pagebound.test"),
                      timeout=10.0) as client:
        run_pipeline(client, "pipeline-out", secret, run_id)


if __name__ == "__main__":
    main()
