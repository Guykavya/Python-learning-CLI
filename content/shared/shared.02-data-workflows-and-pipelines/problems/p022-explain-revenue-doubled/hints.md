## Hint 1

Draw the `orders` table for Sunday after each of the three runs. Run 1 failed at 02:10, but
was anything already committed at that moment? (Look at where `conn.commit()` is.) What does a
plain `INSERT` do with an id that is already in a table without a key? Then ask: besides Ravi,
which parts of the system already re-run work on their own (look at the function names in the
job)?

## Hint 2

Outline:

```
1. run 1: pages 1..k committed, then timeout  -> part of Sunday (say 0.6 copy)
   run 2: retry from page 1, all pages         -> +1 copy
   run 3: manual                               -> +1 copy      => ~2.6x ; Saturday untouched
2. at-least-once is what you can guarantee (scheduler retries, HTTP retries after a timeout,
   resume replays a page, backfills); exactly-once delivery is not possible across crashes
3. idempotent = doing it twice has the same effect as once
   fix: PRIMARY KEY + ON CONFLICT DO UPDATE, or per-day DELETE + INSERT in ONE transaction;
   no commit per page; checkpoint after commit
4. repair: re-run the fixed job for Sunday, or DELETE duplicates keeping one rowid per id
   test: run twice -> identical table and SUM; crash on page 2 -> re-run -> each id once
```
