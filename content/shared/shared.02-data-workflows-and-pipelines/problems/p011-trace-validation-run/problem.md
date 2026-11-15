# Trace: a validation run over messy records

This program runs a small validation pipeline three times. Each record goes through a schema
`check`, then a `transform`; bad records are collected in a quarantine list; at the end the
run is loaded or aborted depending on the share of bad records.

The code has several traps that real pipelines have too: a type check that is too generous,
an `except` that is too narrow, a `finally` block, and two parsers (`Decimal` and
`datetime.fromisoformat`) that accept more, or less, than you might expect.

Work out exactly what the program prints. The program needs no input and no network.

```python
import json
from datetime import datetime
from decimal import Decimal

REQUIRED = {"id": int, "status": str, "amount": str}


def check(rec):
    errors = []
    for field, kind in REQUIRED.items():
        if field not in rec:
            errors.append(f"{field}: missing")
        elif rec[field] is None:
            errors.append(f"{field}: null")
        elif not isinstance(rec[field], kind):
            errors.append(f"{field}: not {kind.__name__}")
    return errors


def transform(rec):
    return {
        "id": rec["id"],
        "status": rec["status"].strip().lower(),
        "amount": Decimal(rec["amount"]),
        "created": datetime.fromisoformat(rec["created_at"]),
    }


def run(name, records, max_bad=0.5):
    good, quarantine = [], []
    try:
        for rec in records:
            errors = check(rec)
            if errors:
                quarantine.append({"id": rec.get("id"), "reason": "; ".join(errors)})
                continue
            try:
                row = transform(rec)
            except (ValueError, KeyError) as e:
                quarantine.append({"id": rec["id"], "reason": type(e).__name__})
                continue
            good.append(row)
            print("OK", row["id"], row["status"], row["amount"], row["created"].isoformat())
    except Exception as e:
        print("CRASH", type(e).__name__, "at id", rec["id"])
        return
    finally:
        for entry in quarantine:
            print("BAD", json.dumps(entry))
    rate = len(quarantine) / len(records)
    print(name, len(good), len(quarantine), "ABORT" if rate > max_bad else "LOAD")


run("batch1", [
    {"id": 1, "status": "Shipped", "amount": "10.50", "created_at": "2024-06-01T10:00:00Z"},
    {"id": "2", "status": "pending", "amount": "5", "created_at": "2024-06-01"},
    {"id": 3, "status": None, "amount": 7},
    {"id": True, "status": " PENDING ", "amount": "0", "created_at": "2024-06-02T09:00:00+05:30"},
    {"id": 5, "status": "shipped", "amount": "3.00"},
])
run("batch2", [
    {"id": 6, "status": "cancelled", "amount": " 4.25 ", "created_at": "2024-06-03"},
    {"id": 7, "status": "shipped", "amount": "4.25", "created_at": "2024-02-30T10:00:00Z"},
    {"id": 8, "status": "shipped", "amount": "1e3", "created_at": "2024-06-03T08:00:00+00:00"},
], max_bad=0.3)
run("batch3", [
    {"id": 9, "status": "shipped", "amount": "2.50", "created_at": "2024-06-04T08:00:00Z"},
    {"id": 11, "status": "shipped", "amount": "1.00"},
    {"id": 10, "status": "shipped", "amount": "12,00", "created_at": "2024-06-04T09:00:00Z"},
    {"id": 12, "status": "shipped", "amount": "8.00", "created_at": "2024-06-04T10:00:00Z"},
])
```

Write your answer in `answer.txt`, one line per printed line.

**Example (a different run)**

```python
run("tiny", [{"id": 1, "status": "Pending", "amount": "2.00", "created_at": "2024-06-01T10:00:00Z"},
             {"id": 2, "amount": "1.00"}])
```

prints

```
OK 1 pending 2.00 2024-06-01T10:00:00+00:00
BAD {"id": 2, "reason": "status: missing"}
tiny 1 1 LOAD
```

(`1 / 2 = 0.5` is not greater than `max_bad=0.5`, so the run is loaded.)
