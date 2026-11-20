## Approach

The six orders and their results:

| # | Order | Reader's `v` | Cache at the end | Later read |
|---|---|---|---|---|
| 1 | read, store, update, delete | OLD | empty | NEW |
| 2 | read, update, store, delete | OLD | empty (the delete removed OLD) | NEW |
| 3 | read, update, delete, **store** | OLD | **OLD** | **OLD (stale)** |
| 4 | update, read, store, delete | NEW | empty | NEW |
| 5 | update, read, delete, store | NEW | NEW | NEW |
| 6 | update, delete, read, store | NEW | NEW | NEW |

Only order 3 is stale: the reader read the database *before* the update and stored *after* the delete. Nobody deletes again, so the old value lives until the TTL ends. No error, no log line.

## Cost

Checking all interleavings of lists of length `a` and `b` takes `C(a + b, a)` runs: 6 here, 10 for 3 + 2 steps. That is small enough to run on every test.

## Another way

Swapping the writer's steps (delete, then update) is worse: the reader can now miss *between* the two writer steps, read OLD and store it, and with an empty cache at that point nothing removes it. Problem p010 removes the race with a generation number that the reader reads **first**.
