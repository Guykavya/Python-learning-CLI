## Model answer

1. **Unsafe.** Old code still uses `total`; the moment the rename runs, its queries fail. *Safe sequence:* add `total_paise` (nullable); deploy code that writes **both** columns; backfill old rows in batches; deploy code that reads `total_paise`; later drop `total` (expand, migrate, contract).
2. **Safe.** Adding a nullable column without a default is a cheap catalogue change in PostgreSQL and SQLite; the old code ignores it. (MySQL may rebuild the table in old versions: check.)
3. **Unsafe.** Existing rows have no value, so the statement fails (or, with a default, may rewrite the table on older databases). The old code inserts rows **without** `status`, which would now be refused. *Safe sequence:* add `status` nullable (or with a default); deploy code that writes it; backfill in batches; add the `NOT NULL` constraint last (when no writer omits it).
4. **Unsafe.** Old servers still read `legacy_ref` and would fail. *Safe sequence:* deploy code that no longer reads or writes the column; wait until every old server is gone; then drop the column in a later migration.
5. **Unsafe as written.** A plain `CREATE INDEX` on PostgreSQL blocks writes to the table while it builds, which on a busy 50-million-row table can last minutes. *Safe:* `CREATE INDEX CONCURRENTLY` (slower, does not block writes; cannot run inside a transaction).
6. **Unsafe.** One statement over 50 million rows holds locks for a long time, bloats the log and may time out or replicate slowly. *Safe:* update in **batches** (for example 1,000 to 10,000 rows per transaction), with a pause, until no row is left.

**Checklist: your answer should mention**
- [ ] the **old code is still running** during a deploy
- [ ] **rename and drop** are done in several steps (expand, migrate, contract)
- [ ] **NOT NULL** is added **last**, after a backfill
- [ ] a nullable new column is **safe**
- [ ] **CREATE INDEX CONCURRENTLY** for a busy PostgreSQL table
- [ ] big data changes in **batches**, not one statement
