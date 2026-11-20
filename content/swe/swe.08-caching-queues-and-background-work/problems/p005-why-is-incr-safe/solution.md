## Approach

The model answer is in `answer.md`. The core is a four-line timeline: A reads 41, B reads 41, A writes 42, B writes 42. Everything else follows: the fix is to do the read and the write in **one** step that nothing can interrupt, and Redis gives you that for free because each command runs alone.

## Cost

`INCR` is O(1) and one network round trip, which is also *faster* than `GET` + `SET` (two round trips).

## Another way

For several commands that must stay together, real Redis offers Lua scripts (`EVAL`), which also run as one atomic step, and `MULTI`/`EXEC` transactions. Optimistic locking with `WATCH` retries the transaction if another client changed the key. All of them are heavier than choosing a single atomic command when one exists.
