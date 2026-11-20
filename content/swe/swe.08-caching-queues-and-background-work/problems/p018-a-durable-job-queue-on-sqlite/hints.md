## Hint 1

Three questions decide the design. (1) How do you make "find the next job" and "claim it" impossible to split between two workers? (2) How does a job come back when its worker dies, if nobody tells the queue? (3) How can `complete` from a worker that lost its job be refused?

## Hint 2

(1) One `UPDATE ... WHERE id = (SELECT ... LIMIT 1) RETURNING *`. (2) Treat `running` with `lease_until <= now` as ready. (3) Add `AND worker = ? AND state = 'running'` to every update and return `cursor.rowcount == 1`.

```text
enqueue: INSERT ... ON CONFLICT (dedupe_key) DO NOTHING RETURNING id
         if no row came back: SELECT id FROM jobs WHERE dedupe_key = ?
fail:    if permanent or attempts >= max_attempts: state dead, finished_at
         else: state queued, run_at = now + retry_in
         both: last_error, lease_until NULL, WHERE id, worker, state running
```
