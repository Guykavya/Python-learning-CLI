# Problem plan: swe.03 Databases for backend engineers (55 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style; SQL-only answers use `QUERY`/`SCHEMA`/`INDEXES` strings in `solution.py` (shared.01 convention). Ids `swe.03.p001`…`p055`.

**Mix:** 18 drill, 20 applied, 13 deep, 4 challenge. **Kinds:** 41 code, 10 trace, 4 explain.
**assessment:** explain = p023, trace = p039, fix = p038, build = p055.
**★ core set:** p003, p004, p009, p013, p019, p020, p023, p024, p025, p030, p033, p037, p038, p039, p041, p045, p046, p048, p050, p051, p055 (outcomes: fix an N+1; change a column without losing data; restore from backup).

**Testing notes**
- **SQLite only** (`sqlite3` and `sqlite://`); PostgreSQL/MySQL parts of the chapter stay "Try it on your machine". The database comes from the test: an in-memory connection, or a file in `tmp_path` when two connections are needed (in-memory databases are private to one connection).
- Every connection the test makes runs `PRAGMA foreign_keys = ON` (off by default in SQLite; p008 teaches exactly this).
- **Query plans:** tests use the chapter's `plan(db, sql)` helper (Ch. 5.3) in `conftest.py` and check **substrings** only: `"SCAN"`, `"SEARCH"`, `"USING INDEX <name>"`, `"USING COVERING INDEX"`, `"USE TEMP B-TREE"`. SQLite changed the wording in 3.36 (`SCAN TABLE t` → `SCAN t`), so never compare whole lines.
- **Counting queries:** `conftest.py` has the chapter's `count_queries(engine)` event listener (Ch. 10.3/10.8) for problems where the learner does not write it.
- **Alembic** runs programmatically: the test builds `alembic.ini`-free `Config()` with `script_location` in `tmp_path`, writes `env.py` and revision files there; revision files do `from solution import upgrade_0002, downgrade_0002` (the learner writes only the functions, using `alembic.op`). `command.upgrade(cfg, "head")` takes ~0.5 s. Use `render_as_batch=True` for SQLite column changes (Ch. 13.6).
- Concurrency problems (p024, p027, p028) use 2–8 threads with separate connections to a `tmp_path` file and `timeout=` on connect; a deadlocked test must fail by timeout in seconds (join with timeout, then assert).
- Async (p053): `asyncio.run(...)` inside a normal test, `sqlite+aiosqlite:///` file in `tmp_path`.

## A. Schema design and normalisation (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Find the update anomaly ✅ | drill | code | `conflicting_facts(rows, key, field)` → keys with more than one value (e.g. one customer with two emails in a flat orders table); empty rows → `{}` |
| 2 | Which normal form is broken? ✅ | drill | trace | `⚠ HAND-TRACE` four small tables with their keys; write `1NF`, `2NF`, `3NF` or `ok` for each and the column that breaks it |
| 3 | Normalise a flat order export ✅ | applied | code | `normalise(rows)` → dict of tables `customers`, `products`, `orders`, `order_lines` with integer ids; no duplicated customer/product rows; joining back reproduces every original row (test re-joins) |
| 4 | Write the bookshop schema ✅ | applied | code | `SCHEMA` SQL with PK, FK, NOT NULL, UNIQUE, CHECK (`qty > 0`, `price_paise >= 0`); the test introspects with `PRAGMA table_info/foreign_key_list` and tries 6 bad inserts, each must fail for the right reason |
| 5 | Money in paise, not floats ✅ | drill | code | `to_paise("12.30")` with `Decimal`, `order_total(lines)` in integer paise; the test shows `0.1 + 0.2` style errors in a float version; rounding rule half-up stated |
| 6 | When is a stored total worth it? ✅ | deep | explain | a slow "orders with totals" page: compare computing the total on read vs storing `order_total` (Ch. 3.6–3.7); checklist: read/write trade-off, keeping it correct (one place writes it, transaction), a reconciliation query |

## B. Constraints and ON DELETE (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 7 | Which constraint said no? ✅ | drill | code | `attempt(db, sql)` (Ch. 4.2) → `"ok"` or `"UNIQUE"`, `"NOT NULL"`, `"CHECK"`, `"FOREIGN KEY"` from the `IntegrityError` text |
| 8 | Foreign keys that do nothing ✅ | drill | code | `connect(path)` must turn on `PRAGMA foreign_keys`; the starter forgets it, so orphan rows slip in; test inserts an order for a missing customer and expects `IntegrityError` |
| 9 | What does this DELETE remove? ✅ | drill | trace | `⚠ HAND-TRACE` schema with `CASCADE`, `SET NULL`, `RESTRICT`; after 4 deletes write the row count of each table, or `error` for the RESTRICT one |
| 10 | Soft delete with a unique email ✅ | deep | code | `deleted_at` column, `active_customers` view, a **partial unique index** `WHERE deleted_at IS NULL` so a deleted email can be re-registered; tests re-register and try a live duplicate |
| 11 | NULL and UNIQUE ✅ | drill | trace | `⚠ HAND-TRACE` 6 inserts into a table with `UNIQUE(email)` including two `NULL`s; write which succeed (SQLite and PostgreSQL both allow many NULLs; Ch. 4.3) |

## C. Indexes and query plans (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 12 | Scan or search? ✅ | drill | code | `uses_index(db, sql, params)` → `True` if any plan line contains `SEARCH ... USING` (incl. covering/primary key); tested on 5 queries |
| 13 | Add the right indexes ✅ | applied | code | `INDEXES` list of `CREATE INDEX` statements for 3 slow queries on a 20,000-row table; test applies them, every query must `SEARCH`, at most 3 indexes allowed (message: "one index per column is not a strategy") |
| 14 | The leftmost-prefix rule ✅ | applied | trace | `⚠ HAND-TRACE` index on `(customer_id, status, created)`; for 8 `WHERE`/`ORDER BY` clauses write `full`, `partial` or `no` index use; confirmed by running the plans when writing the answer |
| 15 | Sort for free with a covering index ✅ | deep | code | an index + `QUERY` so that "latest 20 orders of a customer" plan shows `COVERING INDEX` and no `USE TEMP B-TREE`; results equal the naive query |
| 16 | Partial and expression indexes ✅ | applied | code | case-insensitive email lookup with an index on `lower(email)` and "open tickets" with `WHERE status = 'open'`; the query text must match the index expression (message explains why `LOWER(email)` vs `lower(email)` is fine but `email COLLATE NOCASE` is not) |
| 17 | Why the database ignored your index ✅ | deep | explain | an index on a boolean `is_active` (90% true); explain selectivity, what the planner estimates, when `ANALYZE` changes the choice, and a better index (Ch. 5.8) |
| 18 | Print a plan as a tree ✅ | drill | code | `plan_tree(rows)` turns `EXPLAIN QUERY PLAN` rows `(id, parent, notused, detail)` into an indented text tree; tested on hand-made rows, so it does not depend on the SQLite version |

## D. Transactions (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 19 | An atomic transfer ✅ | drill | code | `transfer(db, src, dst, paise)` inside `with db:`; insufficient funds raises `ValueError` and **both** balances stay; a missing account rolls back the half-done debit |
| 20 | What does the other connection see? ✅ | applied | trace | `⚠ HAND-TRACE` two connections to one file: writes, reads before/after `commit`, a `rollback`; write each printed value (Ch. 6.4) |
| 21 | Import with savepoints ✅ | applied | code | `import_rows(db, rows)` puts each row in a `SAVEPOINT`; bad rows are rolled back alone and reported `(line, error)`; good rows commit once at the end |
| 22 | Place an order without overselling ✅ | applied | code | `place_order(db, sku, qty)` (Ch. 6.2) with `BEGIN IMMEDIATE`: check stock, insert order + lines, decrement stock; insufficient stock leaves no order row |
| 23 | ACID with your own example ✅ | drill | explain | `assessment = "explain"`. Explain atomicity, consistency, isolation and durability using the transfer of p019 and one failure each prevents; checklist from Ch. 6.1 and 6.6 (write-ahead log) |

## E. Isolation and concurrency bugs (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 24 | Stop the lost update ✅ | deep | code | `buy(path, product_id)` from 8 threads with separate connections; read-modify-write loses sales; the fix is one `UPDATE ... SET stock = stock - 1 WHERE id = ? AND stock > 0` and checking `rowcount`; final stock and sold count exact |
| 25 | Optimistic locking with a version column ✅ | applied | code | `update_price(db, id, new, seen_version)` → `True`/`False`; the second writer with an old version gets `False` and changes nothing (Ch. 7.4) |
| 26 | Read the timeline ✅ | deep | trace | `⚠ HAND-TRACE` two transactions interleaved in 8 steps (Ch. 7.3); write the value each `SELECT` returns under READ COMMITTED and under REPEATABLE READ, and name the anomaly |
| 27 | Avoid the deadlock ✅ | deep | code | `transfer_many(accounts, moves)` with one `threading.Lock` per account: always lock in id order; test runs opposite transfers in 2 threads 200 times with a 5 s join timeout; balances conserved |
| 28 | Retry when the database is locked ✅ | challenge | code | `run_in_transaction(connect, work, attempts, sleep)`: retries only `OperationalError("database is locked")` with backoff, re-raises others at once, never retries after a commit; a fake `work` fails twice then succeeds |

## F. SQLAlchemy Core (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 29 | Describe tables with `MetaData` ✅ | drill | code | `make_tables(metadata)` defines `customers` and `orders` with types, FK, `nullable=False`; `metadata.create_all(engine)`; test inspects with `sqlalchemy.inspect` |
| 30 | Insert, select, update, delete in Core ✅ | drill | code | functions over a `Connection`: `add_many`, `by_city`, `rename`, `remove` returning counts; `engine.begin()` for writes |
| 31 | A search built in pieces ✅ | applied | code | `search_books(conn, title=None, max_price=None, author=None, order="title")`; filters added only when given; `order` limited to a whitelist (`ValueError` otherwise) |
| 32 | Close the injection hole ✅ | drill | code | rewrite a `f"... WHERE name = '{name}'"` query with bound parameters; tests with `"' OR 1=1 --"` and `"O'Brien"`; an event listener checks the parameters really were bound |

## G. The ORM (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 33 | Map the shop models ✅ | drill | code | `Customer`, `Order`, `OrderLine` with `Mapped[...]`, `relationship(back_populates=...)`, `cascade="all, delete-orphan"` on lines; creating an order with lines in one `session.add` |
| 34 | The identity map ✅ | applied | trace | `⚠ HAND-TRACE` `s.get(Customer, 1) is s.get(Customer, 1)`, the same across two sessions, after `expire`, after `commit`; write `True`/`False` and how many SELECTs ran (Ch. 9.4) |
| 35 | What will the flush do? ✅ | drill | code | `pending(session)` → `{"new": [...], "dirty": [...], "deleted": [...]}` names from `session.new/dirty/deleted`; checked before and after `flush()` |
| 36 | Top customers, 2.x style ✅ | applied | code | `top_customers(session, n)` with `select(...).join(...).group_by(...).order_by(...)`; ties broken by name; customers without orders excluded |

## H. N+1 queries (Ch. 10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 37 | Count the queries ✅ | drill | code | `count_queries(engine)` context manager collecting SQL via `before_cursor_execute`; `.count` and `.statements`; nested use and listener removal on exit |
| 38 | Fix the N+1 on the orders page ✅ | applied | code | `assessment = "fix"`. `orders_page(session)` (Ch. 10.2) touches `order.customer.name` and `order.lines` for 50 orders: 101 queries. Fix with `selectinload`/`joinedload`; result must equal the naive version and run **≤ 3 queries** (message shows the actual count and the first repeated statement) |
| 39 | Three loading strategies, counted ✅ | deep | trace | `assessment = "trace"`. `⚠ HAND-TRACE` 4 orders with 0–3 lines each; for lazy, `joinedload`, `selectinload` write the number of SQL statements and the number of rows the database returns (joinedload repeats parent rows) |
| 40 | Make N+1 loud ✅ | deep | code | models with `lazy="raise"`; write `report(session)` that works only because it loads what it needs; test also checks that a naive access raises `InvalidRequestError` |

## I. Session lifecycle (Ch. 11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 41 | Return data, not detached objects ✅ | applied | code | starter returns ORM objects from a closed session → `DetachedInstanceError` when the caller reads `customer.orders`; return plain dicts/dataclasses loaded inside the session |
| 42 | Keep going after an error ✅ | deep | code | `add_users(session, emails)` adds each in `session.begin_nested()`; duplicates are skipped and listed; without the savepoint the session is unusable ("rollback first", Ch. 11.4) |

## J. Connection pooling (Ch. 12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 43 | Find the connection leak ✅ | applied | code | `QueuePool(pool_size=2, max_overflow=0, timeout=1)` on a file database; the starter forgets to close on an error path; after 10 calls (some failing) `engine.pool.checkedout() == 0` |
| 44 | Pool arithmetic ✅ | deep | trace | `⚠ HAND-TRACE` `pool_size=3, max_overflow=2`: 8 checkouts and returns in order; write checked-out count, overflow count, and which checkout waits/times out |

## K. Migrations with Alembic (Ch. 13–14)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 45 | The first revision ✅ | applied | code | `upgrade()`/`downgrade()` with `op.create_table` for `products`; the test runs `upgrade head`, inspects columns, then `downgrade base` leaves no table |
| 46 | Add a column and backfill it ✅ | applied | code | add nullable `slug`, fill it from `name` with a data migration (`op.get_bind()`), then make it NOT NULL in batch mode; seeded rows keep their data |
| 47 | Which revisions will run? ✅ | drill | trace | `⚠ HAND-TRACE` a chain 0001→0004 and the current revision; write the revisions `upgrade head`, `downgrade -1`, `downgrade base` run, in order |
| 48 | Change a column without losing data ✅ | challenge | code | Outcome 2. `price REAL` (rupees) → `price_paise INTEGER` by **expand–contract** in three revisions (Ch. 14.2–14.5): add column, backfill in batches, drop the old column in batch mode; the test seeds rows before each step, checks every price survives exactly (`12.30` → `1230`), and that `downgrade` restores rupees |
| 49 | Is this migration safe? ✅ | deep | explain | six migrations (rename in one step, NOT NULL without default on a big table, drop a column the old code still reads, …); say safe/unsafe and the safe sequence; checklist from Ch. 13.8 |

## L. Backups and restores (Ch. 15)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 50 | Back up a live SQLite database ✅ | applied | code | `backup(src, dst)` with `Connection.backup` while another thread writes; copying the file with `shutil` is the wrong way (Ch. 15.2); the backup opens and `PRAGMA integrity_check` is `ok` |
| 51 | The restore drill ✅ | applied | code | Outcome 3. `fingerprint(conn)` (row counts + sums per table, Ch. 15.4) and `restore_and_verify(backup_path, expected)`: restores into a fresh file and raises `RestoreFailed` naming the table that differs; a truncated backup file fails loudly |

## M. NoSQL, async and testing (Ch. 16–18)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 52 | Documents inside SQL ✅ | applied | code | a `products(attrs JSON)` table; `find_by_attr(db, key, value)` with `json_extract`; missing key → not matched; values with quotes |
| 53 | Async top authors ✅ | deep | code | `async def top_authors(session, n)` with `AsyncSession`, `selectinload`, aiosqlite; the test runs it with `asyncio.run`; touching a lazy relationship in async must not happen (`lazy="raise"`) |
| 54 | A test helper that guards against N+1 ✅ | challenge | code | `assert_max_queries(engine, n)` context manager raising `AssertionError` listing the statements when exceeded; used by the test on a good and a bad function (Ch. 18.5) |

## N. Project (Ch. 19)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 55 | The e-commerce database ✅ | challenge | code | `assessment = "build"`. Models `Customer`, `Product`, `Order`, `OrderLine` with constraints; `seed(session)`; `place_order(session, customer_id, items)` that never oversells and stores prices in paise; `orders_with_totals(session)` in ≤ 2 queries; `backup`/`restore_and_verify`. Tests: constraint violations, concurrent-safe stock (sequential with a stale version), query count, fingerprint equal after restore |

## Counts check
Written 2026-11-19 (Sonnet, main session, no subagents). Deviations from the table: no shared `conftest.py` (each test file carries a few lines of `connect`/`plan`/`QueryLog`/Alembic harness, so a problem folder is self-contained); p016's partial index is read in order, so the plan says `SCAN ... USING COVERING INDEX` and the test accepts that (no `TEMP B-TREE`); p038's data has 50 different customers so the naive page really runs 101 statements; p014, p039, p044, p047 answers were produced by running the code (p039 row counts by arithmetic); p026 is pure reasoning about PostgreSQL; p052 uses `json_each` because a JSON path cannot express a key containing a double quote; p027 is a `Bank` class with per-account locks; p028 uses a fake connection plus one real SQLite test; the Alembic tests build revision files in `tmp_path` that import the learner's functions (`from solution import upgrade_0002 ...`); p050's test keeps an uncommitted writer open for one second so that a plain file copy (the bug) is caught; p055 adds `make_engine(path)` with the foreign-key pragma.

Tiers: drill 1, 2, 5, 7, 8, 9, 11, 12, 18, 19, 23, 29, 30, 32, 33, 35, 37, 47 (18); applied 3, 4, 13, 14, 16, 20, 21, 22, 25, 31, 34, 36, 38, 41, 43, 45, 46, 50, 51, 52 (20); deep 6, 10, 15, 17, 24, 26, 27, 39, 40, 42, 44, 49, 53 (13); challenge 28, 48, 54, 55 (4). Total 55.
Kinds: trace 2, 9, 11, 14, 20, 26, 34, 39, 44, 47 (10); explain 6, 17, 23, 49 (4); code 41.

## Risks and open questions

- SQLite version differences: plan wording (handled by substrings), JSON functions (built in since SQLite 3.38; Python 3.11+ on Windows/macOS ships newer; a very old Linux system SQLite would fail p052, so its first test checks `sqlite3.sqlite_version_info >= (3, 38)` with a clear message).
- p026 is about PostgreSQL isolation semantics, which SQLite does not have; it is a pure trace of the chapter's timeline, not run against a database.
- p044 pool arithmetic: confirm the expected numbers by running `QueuePool` when writing `expected.txt`.
- Alembic writes files and imports them: keep each test's `script_location` in `tmp_path` and clear `sys.modules` of revision modules between tests.
