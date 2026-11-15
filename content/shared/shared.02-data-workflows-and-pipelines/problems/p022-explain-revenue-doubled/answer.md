**1. What happened.** The table has no key and the job appends with `INSERT`, committing after
every page. Run 1 loaded and committed the first pages of Sunday, then timed out on a later
page: Sunday now held *part* of its orders. Run 2 (the scheduler's retry) started again at page
1 and loaded all of Sunday: part + 1 copy. Ravi's run added a third full copy. So Sunday has
roughly 1 + 1 + 0.6 copies, which is why revenue is about 2.6x (3.1 / 1.2), not exactly 2 or 3:
the fraction is how far run 1 got. Saturday was loaded exactly once, and no run wrote Saturday
rows, so it is right. `SUM` silently added every copy.

**2. Why "only run once" fails.** A real pipeline can only promise **at-least-once**: every page
is processed one or more times. **Exactly-once** delivery cannot be guaranteed across a network
and a crash, because a process cannot know whether work it did just before dying was saved. Repeats
happen without any human: the scheduler retries a failed job; `call_with_retry` resends a request
after a timeout whose first answer was lost; a resume from a checkpoint that is one page behind
replays that page; a backfill re-processes old days; two schedulers overlap during a deploy.

**3. The fix.** An operation is **idempotent** when doing it twice has the same effect as doing it
once. Make the write idempotent so at-least-once *behaves* like exactly-once:

```sql
CREATE TABLE orders (id INTEGER PRIMARY KEY, day TEXT NOT NULL, amount TEXT NOT NULL);
INSERT INTO orders (id, day, amount) VALUES (?, ?, ?)
ON CONFLICT (id) DO UPDATE SET day = excluded.day, amount = excluded.amount;
```

Or, because the job processes one whole day, replace the day atomically: fetch all pages first,
then in **one** transaction `DELETE FROM orders WHERE day = ?` and insert the day's rows. That also
removes orders that were deleted at the source. Committing per page must go: a crash must leave
the day either old or new, never half. If a checkpoint is added, it is written only after the
commit.

**4. Clean-up and proof.** Repair Sunday by re-running the *fixed* job for that day
(delete+insert replaces it), or deduplicate in place:
`DELETE FROM orders WHERE rowid NOT IN (SELECT MIN(rowid) FROM orders GROUP BY id);`, then
copy the rows into the new keyed table and compare the day's total with the payment provider.
The test that would have caught it: run the job twice for the same day against a
`MockTransport` fake API and assert the table (and `SUM(amount)`) is identical after both runs;
plus a crash test where page 2 raises, then a re-run, asserting each id appears exactly once.
