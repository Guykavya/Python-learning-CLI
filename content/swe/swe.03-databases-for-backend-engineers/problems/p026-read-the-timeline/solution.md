## Approach

| Step | READ COMMITTED | REPEATABLE READ |
|---|---|---|
| 2 (A) | committed value: 100 | snapshot taken now: 100 |
| 5 (B) | T2's 150 is uncommitted and invisible: 100 | 100 |
| 7 (C) | T2 committed before this statement: **150** | still the old snapshot: **100** |
| 8 | the `UPDATE` works on the current row: 150 + 10 | the row was changed by a transaction that committed after the snapshot: **serialization error** |
| 9 | commit: balance 160 | T1 cannot commit its update (it must `ROLLBACK` and retry from the start) |

Answer:

```text
read committed: A=100 B=100 C=150 final=160
repeatable read: A=100 B=100 C=100 final=error
anomaly: non-repeatable read
```

The anomaly is a **non-repeatable read**: T1 read the same row twice (A and C) and got two different values, because T2 committed in between. REPEATABLE READ forbids it; the price is that conflicting writers get an error and must retry. A **dirty read** (B = 150) is not possible in PostgreSQL at any level.

## Complexity

Not applicable.

## Another way

For "read, think, write back" logic at READ COMMITTED, lock the row (`SELECT ... FOR UPDATE`) or use an atomic `UPDATE` (problem 24) instead of relying on an old read.

## Why it matters

The isolation level decides which surprises your code can meet. Knowing the timeline tells you whether to add a lock, use a higher level, or retry on serialization errors.
