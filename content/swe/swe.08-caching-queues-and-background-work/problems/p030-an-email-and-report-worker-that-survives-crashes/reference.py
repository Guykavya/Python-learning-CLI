import csv
import hashlib
import io
import os
import re
import sqlite3
from contextlib import closing

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders    (id INTEGER PRIMARY KEY, customer TEXT, month TEXT, total_cents INTEGER);
CREATE TABLE IF NOT EXISTS reports   (month TEXT PRIMARY KEY, status TEXT NOT NULL, digest TEXT, requested_at REAL);
CREATE TABLE IF NOT EXISTS email_log (key TEXT PRIMARY KEY, to_addr TEXT, state TEXT, provider_id TEXT);
"""
MONTH_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"


def init_db(db_path):
    with closing(sqlite3.connect(db_path, isolation_level=None)) as db:
        db.executescript(SCHEMA)


# ---- the report: deterministic bytes, published atomically
def build_report(rows, month):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["month", "order_id", "customer", "total_cents"])
    for order_id, customer, total in sorted(rows):
        writer.writerow([month, order_id, customer, total])
    return out.getvalue().encode("utf-8")


def write_atomic(path, data, crash):
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "wb") as f:
        f.write(data[: len(data) // 2])
        crash.hit("report:mid-write")
        f.write(data[len(data) // 2:])
        f.flush()
        os.fsync(f.fileno())
    crash.hit("report:before-replace")
    os.replace(tmp, path)


def digest(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


# ---- the API: one transaction for the report row and its job; safe to call twice
class ReportRequest(BaseModel):
    month: str = Field(pattern=MONTH_PATTERN)


def create_app(queue):
    app = FastAPI()

    @app.post("/reports", status_code=202)
    def request_report(body: ReportRequest):
        with closing(queue._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                db.execute("INSERT OR IGNORE INTO reports (month, status, requested_at) VALUES (?, 'queued', ?)",
                           (body.month, queue.now()))
                queue.enqueue_in(db, "report", {"month": body.month}, dedupe_key=f"report:{body.month}")
                db.execute("COMMIT")
            except BaseException:
                db.execute("ROLLBACK")
                raise
            row = db.execute("SELECT status FROM reports WHERE month = ?", (body.month,)).fetchone()
        return {"month": body.month, "status": row["status"], "status_url": f"/reports/{body.month}"}

    @app.get("/reports/{month}")
    def report_status(month: str):
        if not re.match(MONTH_PATTERN, month):
            raise HTTPException(422, "month must look like 2026-10")
        with closing(queue._connect()) as db:
            row = db.execute("SELECT month, status, digest FROM reports WHERE month = ?", (month,)).fetchone()
        if row is None:
            raise HTTPException(404, "no such report")
        return dict(row)

    return app


# ---- the handlers
def make_handlers(queue, out_dir, provider, crash, permanent_error, recipient="finance@example.com"):
    def report(payload, job):
        month = payload.get("month", "")
        if not re.match(MONTH_PATTERN, month):
            raise permanent_error(f"invalid month {month!r}")
        with closing(sqlite3.connect(queue.path, isolation_level=None)) as db:
            rows = [tuple(r) for r in db.execute(
                "SELECT id, customer, total_cents FROM orders WHERE month = ?", (month,))]
        path = os.path.join(out_dir, f"report-{month}.csv")
        write_atomic(path, build_report(rows, month), crash)
        crash.hit("report:after-replace")
        file_digest = digest(path)
        with closing(queue._connect()) as db:                  # status AND follow-up job in ONE transaction
            db.execute("BEGIN IMMEDIATE")
            try:
                db.execute("UPDATE reports SET status = 'ready', digest = ? WHERE month = ?", (file_digest, month))
                queue.enqueue_in(db, "report_email", {"month": month}, dedupe_key=f"report-email:{month}")
                db.execute("COMMIT")
            except BaseException:
                db.execute("ROLLBACK")
                raise
        crash.hit("report:after-status")

    def report_email(payload, job):
        month = payload["month"]
        key = f"report-ready:{month}"
        with closing(sqlite3.connect(queue.path, timeout=10, isolation_level=None)) as db:
            row = db.execute("SELECT state FROM email_log WHERE key = ?", (key,)).fetchone()
            if row and row[0] == "sent":
                return                                          # a duplicate delivery: already done
            db.execute("INSERT OR IGNORE INTO email_log (key, to_addr, state) VALUES (?, ?, 'sending')", (key, recipient))
            crash.hit("email:after-claim")
            message_id = provider.send(recipient, f"Your report for {month} is ready", "See the reports page.",
                                       idempotency_key=key)
            crash.hit("email:after-send")
            db.execute("UPDATE email_log SET state = 'sent', provider_id = ? WHERE key = ?", (str(message_id), key))
            crash.hit("email:after-record")

    return {"report": report, "report_email": report_email}
