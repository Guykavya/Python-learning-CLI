## Approach

The model answer is in `answer.md`. The idea behind it is the most important sentence of this
chapter:

> You cannot make a pipeline run exactly once. You can make running it again harmless.

| Piece | Gives you |
|---|---|
| retries, scheduler re-runs, resume from checkpoint | **at-least-once**: nothing is lost |
| natural key + UPSERT, or delete + insert per partition in one transaction | **idempotent sink**: repeats change nothing |
| both together | the *effect* of exactly-once |

## Check your answer

- Did you trace the three runs and explain the fraction (run 1 committed part of the day
  because of the commit after every page)?
- Did you say why Saturday is unaffected (no run touched it)?
- Did you explain that exactly-once cannot be guaranteed, and name real repeat causes such as
  scheduler retries, HTTP retries after a timeout, checkpoint replays, backfills or overlapping
  runs?
- Did you define idempotent correctly (twice = once), not as "runs only once" or "never fails"?
- Did your fix include a key (`PRIMARY KEY` / unique natural key) with `ON CONFLICT DO UPDATE`,
  or a delete + insert of the whole day in **one** transaction, with the SQL?
- Did you notice that committing per page makes a failed run leave half a day behind, and that a
  checkpoint must come after the commit?
- Did you give a concrete repair (re-run the fixed job, or a dedupe `DELETE` keeping one row per
  id) and a test that runs the job twice and compares the table?

## Another way

Some sinks cannot do UPSERTs (an append-only log, a message queue, an email API). Then the
writer sends an **idempotency key** (here: the order id, or `day + page`) and the receiver keeps
a table of keys it has already applied and drops repeats. This is the same idea moved to the
other side: someone must remember what was already done, by a stable key.
