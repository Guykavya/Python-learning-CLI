## Hint 1

Two workers call `reserve` at the same moment. If your code does "SELECT the next id" and then "UPDATE that id", what can happen between the two statements? Which single SQL statement both finds and changes a row?

## Hint 2

```sql
UPDATE jobs SET state = 'running', attempts = attempts + 1, lease_until = :now + :lease, worker = :worker
WHERE id = (SELECT id FROM jobs
            WHERE (state = 'queued' AND run_at <= :now) OR (state = 'running' AND lease_until <= :now)
            ORDER BY run_at, id LIMIT 1)
RETURNING *
```

For `complete` and `heartbeat`: `UPDATE ... WHERE id = ? AND worker = ? AND state = 'running'`, then `return cursor.rowcount == 1`.
