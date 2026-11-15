import sqlite3
from collections import Counter
from decimal import Decimal, InvalidOperation

STATUSES = {"shipped", "pending", "cancelled"}

CREATE = "CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, status TEXT NOT NULL, amount TEXT NOT NULL)"

UPSERT = """
INSERT INTO orders (id, status, amount) VALUES (:id, :status, :amount)
ON CONFLICT (id) DO UPDATE SET status = excluded.status, amount = excluded.amount
"""


class TooManyBadRecords(Exception):
    """Raised when the share of bad records is above the threshold. Has a .summary attribute."""

    def __init__(self, message: str, summary: dict):
        super().__init__(message)
        self.summary = summary


def problem_with(record, seen_ids: set) -> str | None:
    """The first reason this record is bad, or None. Never raises."""
    if not isinstance(record, dict):
        return "not an object"
    id_ = record.get("id")
    if not isinstance(id_, int) or isinstance(id_, bool) or id_ <= 0:
        return "bad id"
    if record.get("status") not in STATUSES:
        return "bad status"
    amount = record.get("amount")
    if not isinstance(amount, str):
        return "bad amount"
    try:
        value = Decimal(amount)
    except InvalidOperation:
        return "bad amount"
    if not value.is_finite() or value < 0:
        return "bad amount"
    if id_ in seen_ids:
        return "duplicate id"
    return None


def load_with_threshold(conn: sqlite3.Connection, records: list, max_bad_ratio: float = 0.1) -> dict:
    """Skip bad records with reasons; abort (write nothing) if too many are bad."""
    good, failures, seen = [], [], set()
    for index, record in enumerate(records):
        reason = problem_with(record, seen)
        if reason is None:
            seen.add(record["id"])
            good.append({"id": record["id"], "status": record["status"], "amount": record["amount"]})
        else:
            failures.append((index, reason))

    total, bad = len(records), len(failures)
    summary = {"total": total, "loaded": 0, "bad": bad,
               "errors": dict(Counter(reason for _, reason in failures)), "failures": failures}
    if total and bad / total > max_bad_ratio:
        raise TooManyBadRecords(
            f"{bad} of {total} records are bad ({bad / total:.0%} > {max_bad_ratio:.0%})", summary)

    conn.execute(CREATE)
    with conn:                                  # all good rows or none
        conn.executemany(UPSERT, good)
    summary["loaded"] = len(good)
    return summary
