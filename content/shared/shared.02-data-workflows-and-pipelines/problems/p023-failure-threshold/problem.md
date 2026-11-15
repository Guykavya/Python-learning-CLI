# Bad records: skip a few, abort on too many

One broken record must not stop a run of 50,000 good ones: you skip it, record why, and load the
rest. But if **30 %** of a batch is broken, something bigger is wrong (the API changed its
format, you are reading the wrong file), and loading the remaining 70 % would quietly publish a
half-empty report. Good pipelines therefore have a **failure threshold**: skip bad records up to
a limit, and abort the whole batch, loading **nothing**, above it.

Write

```python
class TooManyBadRecords(Exception):          # already written for you in starter.py
    def __init__(self, message: str, summary: dict):
        super().__init__(message)
        self.summary = summary

def load_with_threshold(conn: sqlite3.Connection, records: list, max_bad_ratio: float = 0.1) -> dict:
```

**Checking a record.** Check in this order and use the **first** failing reason:

| reason | when |
|---|---|
| `not an object` | the record is not a `dict` (for example `None`, a string, a number) |
| `bad id` | `"id"` is missing, not an `int`, a `bool`, or not greater than 0 |
| `bad status` | `"status"` is not one of `"shipped"`, `"pending"`, `"cancelled"` |
| `bad amount` | `"amount"` is missing, not a `str`, not parseable by `Decimal`, or negative |
| `duplicate id` | the same id as an earlier **accepted** record in this batch |

Checking must never raise, whatever the record looks like.

**Summary.** Build this dict (`index` is the record's 0-based position in `records`):

```python
{"total": 10, "loaded": 9, "bad": 1,
 "errors": {"bad status": 1},              # reason -> count
 "failures": [(4, "bad status")]}          # (index, reason) in input order
```

**Threshold.** If `bad / total > max_bad_ratio` (strictly greater; an empty batch never aborts):
write nothing at all, leave the table exactly as it was, and raise `TooManyBadRecords` with a
message like `"2 of 10 records are bad (20% > 10%)"` and the summary (with `"loaded": 0`) on its
`summary` attribute.

**Loading.** Otherwise create the table if needed, upsert the good records in **one
transaction**, commit, and return the summary:

```sql
CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, status TEXT NOT NULL, amount TEXT NOT NULL)
```

An id that is already in the table from an earlier batch is updated (`ON CONFLICT (id) DO UPDATE`).

**Example**

```python
good = [{"id": i, "status": "shipped", "amount": "10.00"} for i in range(1, 10)]   # ids 1..9

load_with_threshold(conn, good + [{"id": 10, "status": "lost", "amount": "1.00"}])
# {'total': 10, 'loaded': 9, 'bad': 1, 'errors': {'bad status': 1}, 'failures': [(9, 'bad status')]}
# 1 of 10 is 10 %, which is not MORE than 10 %: the 9 good orders are loaded

load_with_threshold(conn, good[:8] + [None, "oops"])
# TooManyBadRecords: 2 of 10 records are bad (20% > 10%)      nothing is written

load_with_threshold(conn, [good[0], good[0]], max_bad_ratio=0.5)
# {'total': 2, 'loaded': 1, 'bad': 1, 'errors': {'duplicate id': 1}, 'failures': [(1, 'duplicate id')]}
```
