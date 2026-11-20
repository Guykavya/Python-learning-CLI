## Hint 1

For each one ask two questions: does the **old code** keep working while the migration runs and after it? Does the migration **lock** the table for a long time?

## Hint 2

Safe changes are **additive and cheap** (a new nullable column). Unsafe ones break a running reader or writer (rename, drop, NOT NULL without default) or hold a lock while they rewrite a big table (a long `UPDATE`, a plain `CREATE INDEX` in PostgreSQL).

## Hint 3

Patterns: rename = add new, write both, backfill, switch reads, drop old. NOT NULL = add nullable, backfill in batches, then set NOT NULL (or add with a default). Drop = deploy code that no longer reads it first. Index = `CREATE INDEX CONCURRENTLY` (PostgreSQL). Big update = batches.
