# Problem plan: da.07 SQL for analysts (40 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style. Ids `da.07.p001` … `p040`, folder `pNNN-slug`.

**Mix:** 13 drill, 14 applied, 10 deep, 3 challenge. **Kinds:** 31 code, 6 trace, 3 explain.
**assessment:** explain = p024, trace = p013, fix = p031, build = p040.
**★ core set (write first, 16):** p001, p003, p006, p009, p011, p013, p015, p018, p021, p022, p023, p024, p027, p031, p034, p040.

**Testing notes**

- The chapter's company is **LearnLoop** (Ch. 1.2): `users(user_id, signup_at, channel, country)`,
  `events(event_id, user_id, event_time, event_type)` with types `login, view_course, add_to_cart, checkout_start,
  purchase` (not unique per user/time/type), `orders(order_id, user_id, order_time, plan, amount)`; extraction time
  `2025-07-15`. Tests build **tiny inline frames** (3–8 users, 10–30 events) where every row has a purpose, and
  register them on the connection (`con.register("events", df)`), exactly as Ch. 1.2 does.
- **Answer format:** `QUERY = """..."""` in `solution.py` (shared.01 convention); a few problems use a function that
  receives `con` (Ch. 9–10). The test runs the query and compares with a **pandas truth computed in the test** (or a
  hand-made expected table for the tiny data). Compare sorted rows; floats with `pytest.approx`.
- **DuckDB under the runner's 1 GiB cap — measured 2026-11-18, DuckDB 2.0.0:** one or two open in-memory connections
  work; **three open at the same time crashed the process (segfault, exit 139)**, even with `threads=1,
  memory_limit='256MB'`. Opening and closing 50 connections one after another is fine. Rules that follow:
  - every test gets its connection from **one fixture** that does `with duckdb.connect() as con: yield con`;
  - the solution **never opens its own connection** (it returns `QUERY`, or uses the `con` it is given);
  - test files import only `duckdb` and `pandas` (not Polars or pandera as well).
- **DuckDB 2.0 API (measured):** relations have no `fetchone()` (AttributeError), and `con.execute(...).fetchone()` leaves
  an unfinished result so the **next** query on that connection fails with `ResourceInUseException`. Tests use
  `con.execute(QUERY).df()` or `.fetchall()`, never `fetchone()`. The chapter says the same (Ch. 9.1).
- Other measured facts usable in traces: `7 / 2` → `3.5`, `7 // 2` → `3`, `NULLIF(0, 0)` → NULL, `1 / 0` → `inf` (not an
  error, not NULL: a reason to use `NULLIF`); `date_trunc('week', DATE '2025-01-01')` → Monday `2024-12-30`;
  `dayname(DATE '2025-01-01')` → `Wednesday`; `DATE '2025-03-31' + INTERVAL 1 MONTH` → `2025-04-30`;
  `date_diff('month', DATE '2025-01-31', DATE '2025-02-01')` → `1` (counts boundaries);
  `generate_series(DATE '2025-01-01', DATE '2025-01-31', INTERVAL 1 DAY)` → 31 rows; `GROUP BY ALL`, `ORDER BY ALL`,
  `SELECT * EXCLUDE (...)` and `count(*) FILTER (WHERE ...)` work.
- Traces print Python values from `.fetchall()` (tuples of ints/strings/`datetime`), formatted in the trace code; never a
  frame repr (R3).

## A. Analytical SQL patterns and CTEs (Ch. 1–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Conditional aggregation | drill | code | `QUERY`: per channel, users, users with a purchase, purchase rate, using `count(*) FILTER (WHERE …)` or `SUM(CASE …)`; one row per channel |
| 2 | Safe division | drill | code | `QUERY`: purchase rate per country with `NULLIF`; a country with no viewers gives NULL, not `inf` (the measured `1/0` result is quoted in the message) |
| 3 | Buckets by week and month | drill | code | `QUERY`: signups per week (`date_trunc('week', signup_at)`, Monday start) and per month; the expected rows come from a pandas truth |
| 4 | `GROUP BY ALL` and `EXCLUDE` | drill | code | `QUERY` grouping by three columns without repeating them; `SELECT * EXCLUDE (event_id)`; result equal to the spelled-out version |
| 5 | Dates in DuckDB | drill | trace | `⚠ HAND-TRACE` the measured date expressions (week start, day name, month-end plus a month, month difference across a boundary); print each value |
| 6 | A recipe in CTEs | applied | code | `QUERY` with three CTEs (first purchase per user → their channel → revenue by channel and first-purchase month); compared with a pandas version |
| 7 | One CTE per question | deep | explain | Ch. 3.2: rewrite advice for a 60-line nested query; checklist: "one step per CTE", "name by grain", "check each step's row count", "no SELECT * at the end", "filter early" |

## B. Window functions (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 8 | Three kinds of rank | drill | trace | `⚠ HAND-TRACE` `row_number`, `rank`, `dense_rank` and `ntile(2)` over 6 amounts with a tie (order by amount desc, then order_id) |
| 9 | Previous and next event | drill | code | `QUERY`: per user, each order with the previous order time (`lag`) and days since it; first order NULL |
| 10 | Frames: rows or range? | deep | trace | `⚠ HAND-TRACE` `sum(amount) OVER (ORDER BY day ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)` against `RANGE` on data with two rows on the same day, and the default frame |
| 11 | Running total and 7-day average | applied | code | `QUERY`: daily revenue, running total, and a 7-row moving average over a **complete** calendar (days without orders = 0, Ch. 5.1); compared with pandas `cumsum`/`rolling` |
| 12 | Share of the total | applied | code | `QUERY`: revenue per plan and country, share of the grand total and cumulative share in descending order; shares sum to 1 |
| 13 | Top N per group | drill | trace | `assessment = "trace"`. `⚠ HAND-TRACE` the rows kept by `QUALIFY row_number() OVER (PARTITION BY country ORDER BY amount DESC, order_id) <= 2` on 9 orders |
| 14 | The latest row per user | applied | code | `QUERY` returning each user's latest event (ties by `event_id`), with `QUALIFY` or `arg_max`; equals the pandas `sort` + `drop_duplicates` truth |
| 15 | Gaps and islands: login streaks | deep | code | `QUERY`: each user's longest run of consecutive login days (several logins on a day count once); `⚠ HAND-TRACE` the 4-user test data (Ch. 4.8) |
| 16 | Sessions from events | deep | code | `QUERY`: a new session when the gap is over 30 minutes; sessions per user and average length; the measured lag-gap example is the first test (Ch. 4.9) |

## C. Calendars and active users (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 17 | A complete calendar | drill | code | `QUERY`: one row per day of June 2025 with logins (0 when none), using `generate_series`; exactly 30 rows |
| 18 | DAU, WAU, MAU | applied | code | `QUERY`: for each day, distinct users active that day, in the 7 days ending that day, and in the 30 days ending that day; compared with a pandas loop truth on 5 users |
| 19 | Month over month | applied | code | `QUERY`: monthly revenue, previous month, change and percentage change (`lag`), first month NULL |
| 20 | Distinct users do not add up | drill | trace | `⚠ HAND-TRACE` the sum of three daily active-user counts against the 3-day distinct count, for 4 users |

## D. Cohort retention (Ch. 6) — the learning outcome

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 21 | Signup cohorts | drill | code | `QUERY`: cohort month (`date_trunc('month', signup_at)`), cohort size; a user with no events still counts in the size |
| 22 | The retention table | applied | code | `QUERY` with columns `cohort, month_number, active_users, cohort_size, retention` (Ch. 6.2); month 0 retention ≤ 1; compared with a pandas truth |
| 23 | The immature cell is NULL, not 0 | deep | code | extend p022: cells after the extraction date (`2025-07-15`) must be NULL; a cohort from June has month 2 = NULL; the "0%" mistake fails with the Ch. 6.4 message |
| 24 | Reading a retention table | applied | explain | `assessment = "explain"`. Given a small retention matrix, explain what each axis means, why the bottom-right is empty, why the pooled curve must only use mature cells; checklist: "cohort = signup month", "month number since signup", "immature cells", "pooled curve weights", "do not compare raw counts" |
| 25 | Day-N retention | applied | code | `QUERY`: share of users active exactly on day 1, 7 and 30 after signup, counting only users whose day N is before the extraction time |
| 26 | Retention by channel | challenge | code | `QUERY`: month-1 retention per channel with the cohort size next to it and NULL for channels with too few mature users (< 3, stated) (Ch. 6.7) |

## E. Funnels and user states (Ch. 7–8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 27 | First time of each step | applied | code | `QUERY`: one row per user with the first time of each funnel step (`min(...) FILTER`), NULL when never reached |
| 28 | Unordered or ordered funnel? | deep | code | `QUERY` for an **ordered** funnel (each step after the previous one); a user who purchased before viewing is counted in the unordered funnel but not the ordered one (Ch. 7.3) |
| 29 | Time between steps | applied | code | `QUERY`: median hours from `add_to_cart` to `purchase` for users who did both, per channel (`median()` or `quantile_cont`) |
| 30 | A conversion window | deep | code | `QUERY`: users who purchased within 7 days of their first view; a purchase on day 8 does not count; boundary exactly at 7 days counts (stated) |
| 31 | Fix the funnel that grows | deep | code | `assessment = "fix"`. Given a funnel `QUERY` that joins events to orders per user (fan-out) and counts rows, so later steps exceed earlier ones; tests: each step ≤ the previous one, counts are distinct users, equal to the pandas truth |
| 32 | New, retained, resurrected, churned | challenge | code | `QUERY`: for each user and month, the state of Ch. 8.1 (`new`, `retained`, `resurrected`, `churned`); hand-made 5-user timeline as the first test |
| 33 | Classify the states by hand | deep | trace | `⚠ HAND-TRACE` the four-state label of 4 users over 4 months with the chapter's rules (Ch. 8.1, copied into `problem.md`) |

## F. DuckDB with pandas and Parquet (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 34 | Query a DataFrame, get a DataFrame | drill | code | `revenue_by_plan(con, orders)`: registers `orders`, runs one query, returns `con.execute(...).df()` sorted; no `fetchone` (measured trap) |
| 35 | Read only what you need from Parquet | applied | code | `june_revenue(con, path)`: the test writes a Parquet file into `tmp_path`; the solution queries it with `read_parquet` selecting two columns and filtering by date |
| 36 | Partitioned files | applied | code | `revenue_by_country(con, folder)`: the test writes a hive-partitioned dataset (`country=IN/…`) into `tmp_path`; the solution reads it with `hive_partitioning = true`; the partition column is in the result |
| 37 | pandas or DuckDB? | drill | explain | Ch. 9.6: when each is the better tool; checklist: "data fits in memory", "SQL readability", "Parquet scans", "measure", "one source of truth for logic" |

## G. Checking your SQL, and the project (Ch. 10–11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 38 | Assert the grain of a query | applied | code | `assert_grain(con, sql, key)` raises when the result has duplicate keys or NULL keys, naming up to 3 duplicates (Ch. 10.1) |
| 39 | A test with a tiny table | deep | code | write `test_retention_query()` style check: `retention_on(con, users, events, cutoff)` from Ch. 10.3 on a 3-user table whose answer you can count; the test calls the learner's function with two different tiny tables |
| 40 | Business questions answered in SQL | challenge | code | `assessment = "build"` (project). `QUERIES` dict with five named queries (monthly revenue and growth, retention table with NULL immature cells, ordered funnel by channel, top 2 courses per country, active-user states by month); each checked on the inline LearnLoop data against a pandas truth, with `assert_grain` on its stated key |

## Counts check

Tiers: drill 1, 2, 3, 4, 5, 8, 9, 13, 17, 20, 21, 34, 37 = 13 ·
applied 6, 11, 12, 14, 18, 19, 22, 24, 25, 27, 29, 35, 36, 38 = 14 ·
deep 7, 10, 15, 16, 23, 28, 30, 31, 33, 39 = 10 · challenge 26, 32, 40 = 3. Total 40.
Kinds: trace 5, 8, 10, 13, 20, 33 = 6 · explain 7, 24, 37 = 3 · code 31.
Assessments: explain p024, trace p013, fix p031, build p040.

## Risks and open questions

- **DuckDB connections under the cap** (see Testing notes): this is the one thing most likely to make a correct answer
  crash. Put the connection fixture in a shared `conftest.py` and copy it unchanged into every problem.
- Ch. 6 retention definitions (month number, what "active" means, how the extraction date cuts cells) must be copied
  exactly from Ch. 6.2–6.4 when writing p021–p026; check one cell by hand per test.
- p036: hive partition reading syntax changed across DuckDB versions (`hive_partitioning=1` vs `true`); run it once on
  the installed 2.0.0 before writing `solution.md`.
- DuckDB returns `datetime.datetime` even for `date_trunc` on a `DATE` (measured); tests normalise with `pd.to_datetime`.
