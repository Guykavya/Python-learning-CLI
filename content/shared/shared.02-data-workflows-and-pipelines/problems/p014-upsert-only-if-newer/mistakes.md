- `INSERT OR REPLACE`. It is idempotent for the same batch, but a stale version that arrives
  later overwrites newer data. "Last write wins" is not "newest version wins".
- `DO UPDATE` without a `WHERE`: same problem as `INSERT OR REPLACE`.
- `>=` instead of `>`. The table looks right, but every re-run reports rows as "updated" and,
  with a different status at the same timestamp, the stored version flips.
- Forgetting to set `updated_at = excluded.updated_at`. The data changes but the stored time does
  not, so a later stale row (newer than the old time) can overwrite it.
- Writing `WHERE updated_at > excluded.updated_at` (the sides swapped): only stale rows win.
- Counting `len(rows)` instead of `cursor.rowcount`. The summary of a run should say how many rows
  really changed; re-runs should report 0.
- Not committing. Your own connection sees the rows, so it looks fine, but another process (or
  the next run) does not, and closing the connection throws the work away.
- Building the SQL with f-strings. A value with a quote breaks it, and it is SQL injection.
