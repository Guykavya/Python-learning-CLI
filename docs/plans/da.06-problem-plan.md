# Problem plan: da.06 Analytical thinking and metric correctness (45 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `da.06.p001` … `p045`, folder `pNNN-slug`.

**Mix:** 15 drill, 16 applied, 10 deep, 4 challenge. **Kinds:** 34 code, 7 trace, 4 explain.
**assessment:** explain = p022, trace = p041, fix = p033, build = p045.
**★ core set (write first, 18):** p001, p005, p008, p009, p010, p013, p015, p016, p020, p022, p024, p029, p033, p036, p037, p038, p039, p045.

**Testing notes**

- The chapter's company is **QuickFix** (Ch. 1.1): `customers`, `jobs` (`job_id, customer_id, created_at, status,
  started_at, completed_at, cancelled_at, quote_total`), `items`, `payments`, `refunds`; timestamps in UTC; the business
  works in IST (UTC+5:30); data cut at `2025-04-05 00:00` UTC. Tests build **tiny inline versions** (5–12 jobs) where each
  row is there for a reason (a job created 31 Jan 23:00 UTC, a cancelled-after-start job, a job with two payments, …),
  so every expected number is countable by hand. No hard-coded numbers from `make_business` (R3).
- SQL problems (Ch. 10): `QUERY = """..."""` in `solution.py` (shared.01 convention). The test loads the inline tables
  into `sqlite3.connect(":memory:")` with timestamps as `"%Y-%m-%d %H:%M:%S"` text (exactly as Ch. 10 does), runs the
  query and compares with a pandas truth computed in the test. Parameters with `?` where a period is involved.
- Reconciliation problems compare **sets of `job_id`s**, not only totals: the outcome is "trace a mismatch down to the
  records", so the test checks the exact ids and the reason labels.
- Half-open intervals `[start, end)` everywhere; every date test includes a timestamp exactly on a boundary.
- Traces print counts, sums, sorted id lists; never a frame repr (R3).

## A. Three numbers and grain (Ch. 1–2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Check the grain ✅ | drill | code | `check_grain(df, key, name="")` returns `True` or raises `ValueError` listing up to 5 duplicated key values and the duplicate count; key may be one column or several |
| 2 | Find the grain yourself ✅ | deep | code | `candidate_keys(df, max_cols=2)` → all minimal column sets that are unique and have no missing values, sorted; supersets of a key are not listed |
| 3 | State the grain ✅ | drill | explain | five table descriptions (jobs, job line items, daily payment totals, a customer snapshot, an event log); write "one row is …" and the key for each; checklist from Ch. 2.3 (entity, event, snapshot, aggregate) |
| 4 | The grain of a result ✅ | drill | trace | `⚠ HAND-TRACE` after a `groupby`, a `merge` to items and a `drop_duplicates`, print `df.duplicated(subset=…).any()` for three candidate keys |

## B. Keys (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 5 | What relationship do two tables have? ✅ | applied | code | `relationship(left, right, left_key, right_key)` → `"1:1"`, `"1:m"`, `"m:1"` or `"m:m"`, plus orphan counts on each side (Ch. 3.4) |
| 6 | Orphans ✅ | drill | code | `orphans(jobs, customers)` → jobs whose customer is missing and customers with no job, as sorted id lists |
| 7 | Natural or surrogate key? ✅ | drill | explain | Ch. 3.2: when a natural key (phone number, email, invoice number) breaks, and why a surrogate key needs a uniqueness rule on the natural columns too; checklist: "changes over time", "reused", "not unique", "surrogate is meaningless", "keep a unique constraint" |

## C. Join fan-out (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 8 | See the fan-out ✅ | drill | trace | `⚠ HAND-TRACE` jobs (4 rows) merged to items (7 rows): row count, `quote_total` sum after the merge, and `job_id.nunique()` |
| 9 | Three answers from one bad join ✅ | applied | code | given the fanned-out table, compute the correct job count, job value and item count (`nunique`, sum per job first) — `correct_totals(joined)` |
| 10 | Aggregate before you join ✅ | drill | code | `paid_per_customer(jobs, payments)` pre-aggregates payments per job, then joins; total paid equals `payments.amount.sum()` for jobs that exist |
| 11 | Predict the explosion ✅ | deep | code | `rows_after_join(a, b, key)` predicts the inner-join row count from key counts **without merging** (sum of products); equals `len(a.merge(b))` on random data |
| 12 | Guard the row count ✅ | drill | code | `assert_rows_unchanged(before, after, label)` raises with "fan-out in <label>: 120 → 134 rows" when they differ (Ch. 13 toolkit) |

## D. Counting (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 13 | Rows, values, distinct values ✅ | drill | code | `three_counts(payments)` → payment rows, payments with a method recorded, distinct paying customers; each with its own message |
| 14 | Distinct counts do not add up ✅ | drill | trace | `⚠ HAND-TRACE` distinct customers per month for Jan–Mar, their sum, and distinct customers for the quarter (Ch. 5.2) |
| 15 | Which denominator? ✅ | applied | code | `completion_rates(jobs, start, end)` → completed / created, completed / started, completed / (completed + cancelled + failed) for jobs created in the period; the three differ on the test data |

## E. Averages (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 16 | Average job value by city ✅ | drill | code | `avg_job_value(jobs, customers)` overall (weighted by jobs) and per city; the mean of city averages is a separate, failing answer with a message |
| 17 | Per job or per customer? ✅ | applied | code | `items_per_job` vs `items_per_customer`; the unit of analysis changes the answer; both checked by hand-counted data |
| 18 | Simpson's paradox among technicians ✅ | deep | code | `completion_by_tech(jobs)` per job type and overall; `paradox(jobs, a, b)` is `True` on the test data where technician A wins in every type but loses overall |
| 19 | Weighted or unweighted ✅ | applied | trace | `⚠ HAND-TRACE` simple mean of three city averages vs the weighted mean, with 2 decimals (Ch. 6.3) |

## F. Metric definitions (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 20 | A metric as code ✅ | applied | code | a `Metric` dataclass (name, numerator, denominator, date_basis, exclusions) and `compute(metric, jobs, start, end)`; two registered metrics computed on the inline data |
| 21 | One name, four definitions ✅ | applied | code | `completed_in_february(jobs, definition)` for four definitions (by created, by started, by completed, IST vs UTC); each gives a different count on the test data and a stated value |
| 22 | Write a definition nobody can misread ✅ | applied | explain | `assessment = "explain"` (learning outcome). Define "monthly completion rate" for QuickFix; checklist from Ch. 7.1–7.4: numerator, denominator, date basis, time zone, half-open period, statuses included/excluded, immature jobs, owner and version |
| 23 | Lint a metric definition ✅ | deep | code | `lint_definition(spec: dict)` → list of problems: missing required fields, vague words (`"active"`, `"recent"`, `"valid"`) without a rule, closed date intervals, no time zone |

## G. Dates (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 24 | Half-open periods ✅ | drill | code | `in_period(s, start, end)` = `start <= t < end`; boundary timestamps at exactly `end` excluded, at `start` included; NaT → False |
| 25 | `between` versus half-open ✅ | drill | trace | `⚠ HAND-TRACE` counts of 6 timestamps (including `23:59:59.5` and midnight) using `between(start, end)` with `end = "2025-02-28"`, and with half-open `[Feb 1, Mar 1)` |
| 26 | Which day is it in India? ✅ | applied | code | `jobs_per_ist_day(jobs)`: convert UTC to IST (`tz_localize("UTC").tz_convert("Asia/Kolkata")`, or +5:30) and count by local date; a job at 20:00 UTC moves to the next day |
| 27 | Immature cohorts ✅ | applied | code | `mature_completion_rate(jobs, cut, min_age_days)` excludes jobs too young to have finished; the naive rate (all jobs) is lower on the test data; both returned |
| 28 | The partial month ✅ | drill | code | `monthly_counts(jobs, cut)` adds `is_partial` for the month containing the cut; the partial month is not compared with full ones (stated) |

## H. Status and lifecycle (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 29 | Does the status agree with the timestamps? ✅ | applied | code | `lifecycle_problems(jobs)` → `(job_id, problem)` pairs: completed without `completed_at`, cancelled after start, completed before started, pending with a completion time (Ch. 9.2) |
| 30 | What was pending last Monday? ✅ | deep | code | `pending_on(jobs, when)` from the timestamps, not today's `status` (Ch. 9.3); a job completed after `when` was pending then |
| 31 | Status on a date ✅ | deep | trace | `⚠ HAND-TRACE` the state (`"not yet created"`, `"waiting"`, `"in progress"`, `"done"`, `"cancelled"`) of 6 jobs at a given moment, using the chapter's rules |

## I. The same questions in SQL (Ch. 10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 32 | Three counts in SQL ✅ | applied | code | `QUERY` returning `rows, with_method, distinct_customers` from `payments` (`COUNT(*)`, `COUNT(col)`, `COUNT(DISTINCT col)`) |
| 33 | Fix the query that doubles revenue ✅ | deep | code | `assessment = "fix"`. Given `QUERY` joining jobs to items **and** payments before summing; tests: revenue equals the pandas truth, one row per month, no fan-out (Ch. 10.3) |
| 34 | `AVG` and `NULL` ✅ | applied | code | `QUERY` for the average rating per technician where `NULL` means "not rated"; `AVG` skips NULL; the `COALESCE(rating, 0)` mistake gets its own failing case |
| 35 | Two engines, one answer ✅ | applied | code | `both_ways(name, pandas_value, sql, con)` runs the SQL and raises with both numbers when they differ by more than 0.005 (Ch. 10.6) |

## J. Reconciliation (Ch. 11–12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 36 | Compare two sets of keys ✅ | drill | code | `compare_keys(a, b, name_a, name_b)` → dict with `only_a`, `only_b`, `both` (sorted) and counts |
| 37 | Find the records behind the gap ✅ | deep | code | the outcome. `explain_gap(dashboard, sql_result)` (row-level tables with `job_id` and `amount`) → the job ids causing the difference and their contribution; contributions sum to the gap |
| 38 | A bridge ✅ | applied | code | `bridge(start_label, start_value, steps, end_label, end_value)` → text table; raises when the steps do not add up (Ch. 11.4) |
| 39 | Total versus completed plus pending ✅ | challenge | code | the worked case of Ch. 12: `volume_bridge(jobs, start, end)` → the sets T (created in period), C (completed, by start date), P (pending), and every job in only one set with its reason label (`"created earlier, started in period"`, `"cancelled"`, …); the bridge closes |
| 40 | Why completed + pending ≠ total ✅ | deep | explain | in your words, using the Ch. 12 result: different date bases, statuses outside both sets, the cut; checklist: "different date basis", "cancelled and failed", "jobs from earlier periods", "a bridge explains each step" |
| 41 | Classify jobs into the sets ✅ | deep | trace | `assessment = "trace"`. `⚠ HAND-TRACE` for 7 jobs with given timestamps and statuses, print which of T, C, P each is in and the reason label of those in only one set (the chapter's `why_only_T`/`why_only_C` rules, copied into `problem.md`) |

## K. Toolkit and project (Ch. 13–14)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 42 | `safe_join` ✅ | applied | code | `safe_join(left, right, on, how="left", validate="m:1", label="")`: validates, checks the row count, raises with the label |
| 43 | A metrics table ✅ | challenge | code | `metrics_table(ctx, specs, months)` from `MetricSpec` definitions (Ch. 14.2–14.3): one row per metric and month with numerator, denominator and value; each cell checked against a slow loop |
| 44 | Cash against work ✅ | challenge | code | `cash_vs_work(jobs, payments, refunds, month)` → work value (completed jobs) vs cash (payments − refunds by payment date) and a bridge of the difference by reason (paid in advance, paid later, refunded) (Ch. 14.5) |
| 45 | Metric document and reconciliation report ✅ | challenge | code | `assessment = "build"` (project). `definition_doc(specs)` → Markdown with one section per metric (all Ch. 7 fields), and `reconciliation_report(tables, month)` → the two bridges of Ch. 14.4–14.5 as text; tests check every metric section has all fields and both bridges close on the inline data |

## Counts check

Tiers: drill 1, 3, 4, 6, 7, 8, 10, 12, 13, 14, 16, 24, 25, 28, 36 = 15 ·
applied 5, 9, 15, 17, 19, 20, 21, 22, 26, 27, 29, 32, 34, 35, 38, 42 = 16 ·
deep 2, 11, 18, 23, 30, 31, 33, 37, 40, 41 = 10 · challenge 39, 43, 44, 45 = 4. Total 45.
Kinds: trace 4, 8, 14, 19, 25, 31, 41 = 7 · explain 3, 7, 22, 40 = 4 · code 34.
Assessments: explain p022, trace p041, fix p033, build p045.

## Risks and open questions

- Re-read Ch. 9.2 (`lifecycle_problems`), Ch. 12.3 (`why_only_T`, `why_only_C`) and Ch. 14.2 (`MetricSpec`) when writing
  p029, p039, p041, p043: the labels and field names must match the chapter.
- p026: `tz_convert("Asia/Kolkata")` needs the time-zone database (`tzdata` is a dependency on Windows; present on Linux).
- SQLite has no real timestamp type; date comparisons work on the text only because the format is fixed-width. State
  the format in each SQL problem and use `substr`/`strftime` like the chapter does.
- The inline datasets carry the whole teaching load here: write one shared `conftest.py` dataset (≈ 12 jobs with a
  comment per row saying why it exists) and reuse it, so the hand counts are checked once.
