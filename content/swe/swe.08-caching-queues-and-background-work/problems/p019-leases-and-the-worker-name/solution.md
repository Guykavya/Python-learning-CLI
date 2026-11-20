## Approach

Every change is one `UPDATE` whose `WHERE` states exactly when the change is allowed, and the caller learns the outcome from `rowcount` (or from `RETURNING`).

```python
def reserve(db, worker, now, lease=30.0):
    row = db.execute(
        "UPDATE jobs SET state = 'running', attempts = attempts + 1, lease_until = ?, worker = ? "
        "WHERE id = (SELECT id FROM jobs WHERE "
        "            (state = 'queued' AND run_at <= ?) OR (state = 'running' AND lease_until <= ?) "
        "            ORDER BY run_at, id LIMIT 1) "
        "RETURNING *",
        (now + lease, worker, now, now),
    ).fetchone()
    return dict(row) if row else None


def complete(db, job_id, worker, now):
    cur = db.execute("UPDATE jobs SET state = 'done', lease_until = NULL "
                     "WHERE id = ? AND worker = ? AND state = 'running'", (job_id, worker))
    return cur.rowcount == 1


def heartbeat(db, job_id, worker, now, lease=30.0):
    cur = db.execute("UPDATE jobs SET lease_until = ? WHERE id = ? AND worker = ? AND state = 'running'",
                     (now + lease, job_id, worker))
    return cur.rowcount == 1
```

SQLite runs each statement under its write lock, so the inner `SELECT` and the `UPDATE` cannot be split by another worker. The worker-name check means only the **current** lease holder can finish or extend a job; a worker that was paused past its lease learns it lost the job (`False`) instead of silently overwriting the new owner's state.

## Complexity

O(log n) per claim with an index on `(state, run_at)`, O(n) without one. The statements are short, so SQLite's single writer handles thousands of claims per second (machine-specific).

## Another way

**Optimistic claim:** `SELECT` a candidate id, then `UPDATE jobs SET ... WHERE id = ? AND (state = 'queued' OR lease_until <= ?)` and check `rowcount`; if 0, someone was faster: try again. On PostgreSQL the standard form is `SELECT ... FOR UPDATE SKIP LOCKED` inside a transaction, which lets many workers claim different rows without waiting for each other.
