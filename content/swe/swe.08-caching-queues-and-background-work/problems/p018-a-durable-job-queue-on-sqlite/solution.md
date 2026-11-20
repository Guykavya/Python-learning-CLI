## Approach

Each job is a row; its `state` moves `queued -> running -> done`, or back to `queued` (retry or expired lease), or to `dead`. Three ideas make it safe:

1. **Claim in one statement.** `UPDATE ... WHERE id = (SELECT ...) RETURNING *` finds and claims the job under SQLite's write lock, so two workers can never claim the same row (PostgreSQL: `SELECT ... FOR UPDATE SKIP LOCKED`).
2. **Leases.** A running job whose `lease_until` has passed is ready again: a crashed worker cannot lose a job (at-least-once).
3. **Owner checks.** `complete` and `fail` include `AND worker = ? AND state = 'running'`, so a worker whose lease expired cannot overwrite the new owner's work.

The full code is `reference.py`:

```python
def reserve(self, worker, *, lease=30.0):
    now = self.now()
    with closing(self._connect()) as db:
        row = db.execute(
            "UPDATE jobs SET state = 'running', attempts = attempts + 1, lease_until = ?, worker = ? "
            "WHERE id = (SELECT id FROM jobs WHERE "
            "            (state = 'queued' AND run_at <= ?) OR (state = 'running' AND lease_until <= ?) "
            "            ORDER BY run_at, id LIMIT 1) "
            "RETURNING *",
            (now + lease, worker, now, now),
        ).fetchone()
        return dict(row) if row else None
```

`enqueue` uses `INSERT ... ON CONFLICT (dedupe_key) DO NOTHING RETURNING id`; when the key existed, no row comes back and a `SELECT` finds the existing id. `NULL` keys never conflict, so jobs without a key are never merged.

## Complexity

`reserve` is O(log n) with an index on `(state, run_at)` (the chapter adds one), O(n) without. Every call opens a connection, which is simple and safe for many threads but costs about a millisecond (machine-specific).

## Another way

The chapter's version adds a `queue` column (separate queues for e-mails and reports), `heartbeat` to extend a lease, `requeue_dead` for operators, `stats` for monitoring, and an extra rule in `reserve`: a job whose lease expired **on its last attempt** goes straight to `dead`. Production libraries on PostgreSQL (Procrastinate, and others) follow the same design.
