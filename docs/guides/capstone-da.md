# DA capstone: an end-to-end analysis with reconciled numbers

You have finished (or nearly finished) the Data Analyst track (da.01 to da.13). The capstone
proves you can combine it: take a large, messy, public dataset, clean it, define the metrics,
query it, test your findings honestly, and deliver a dashboard and a written report that a
manager could act on, with every number reconciled. You choose the question. Nobody gives
you a solution. The checklist at the bottom is how you (or a reviewer) decide it is done.

Syllabus line: *End-to-end analysis of a large public dataset with reconciled metrics,
dashboard and written report.*

## Rules

- **It is yours.** Your question, your analysis, your words. Use the course chapters and the
  official docs, not generated analysis. A reviewer (a friend, or Claude in tutor mode)
  reads and comments; they do not rewrite it.
- **Own folder, own repo.** Keep it outside `my-work/`, with its own git history on your
  personal GitHub. Never a company account, company remote or company data. Never data
  with personal information about real, identifiable people unless it is a published open
  dataset whose licence allows your use.
- **Public data, downloaded once.** The dataset must be public and legally reusable.
  Download it once, record the URL, the date and the licence in `DATA.md`, and from then on
  work **offline from the local copy**. Keep the raw file untouched (read-only) in
  `data/raw/`; every cleaning step is code that produces `data/clean/`.
- **Large means it hurts a little.** At least **500,000 rows** in the main table, or several
  joined tables that together reach it. Small enough for your laptop (a few hundred MB),
  large enough that you must care about types, memory and Parquet (da.03, da.07).
- **No dataset yet?** Take the default: a public city dataset with events over time
  (taxi or bike-share trips, 311 service requests, road collisions, flights). It has dates,
  places, categories, missing values, duplicates and a natural business question.
- **Time-box.** Plan 3-4 weeks of part-time work. Write the question note first (below).

## Pick a question

A good question is **specific, decision-shaped and answerable with the data**. "Explore the
data" is not a question. Examples:

- Which kinds of 311 requests are closed slowest, did that change over three years, and
  which district is the outlier after adjusting for request type?
- Did a fare or pricing change coincide with fewer trips, or is it seasonality?
- Which routes or airlines have the worst delays, and is the ranking stable or noise?
- Where and when should a city send inspectors, given complaints per head and response time?

If you cannot decide in a day, take the default: **service-request response times** (what
is the metric, who is slow, is it getting worse, what would you change?).

## Step 0: the question note (1-2 pages, before any analysis)

Write `QUESTION.md` and keep it in the repo:

1. The decision this analysis supports, and who makes it.
2. The primary question and at most two secondary questions.
3. The metrics, each defined with a **formula, a grain and a filter** (da.06), including
   what counts as "closed", "active", "late"... in plain words.
4. The data: source, columns you expect to use, the grain of every table, known problems.
5. The hypotheses you will test **before** looking (da.08): what you expect and what result
   would change your mind.
6. The risks: three biggest unknowns (a changed definition? missing years?) and what you
   will try first.
7. What you are deliberately *not* analysing.

Bring `QUESTION.md` to the reviewer before you write much code.

## Requirements

Tick every **Must**. Aim for most **Should** items. **Stretch** is optional.

### A. Data acquisition and documentation

- **Must:** `DATA.md`: source URL, download date, licence, file sizes, a checksum (SHA-256)
  of every raw file, and the data dictionary (every column: meaning, type, unit, allowed
  values).
- **Must:** raw files are never edited; a script rebuilds everything downstream from them.
- **Must:** a **data-quality profile** of the raw data (da.05): missing values per column,
  duplicates, impossible values, inconsistent categories, date range and gaps, with counts.
- **Should:** the profile is produced by a function you can re-run on a refreshed extract.
- **Stretch:** a second source joined in (weather, population, holidays) with the join key,
  grain and fan-out checked.

### B. Cleaning and reasoning about missing data

- **Must:** a **cleaning log**: every rule, how many rows it touched, and why it is safe.
  Rows are flagged or moved to a quarantine file, not silently dropped.
- **Must:** a missing-data decision for each important column (MCAR, MAR, MNAR reasoning,
  da.05) and a sensitivity check: how much does the headline result move under another
  reasonable choice?
- **Must:** types fixed on load (dates, categories, nullable integers), and the clean data
  written to **Parquet**.
- **Must:** **reconciliation after cleaning**: raw row count - removed rows = clean row
  count, and key totals match the raw data before and after.
- **Should:** every rule is a small tested function (pytest) with a case it must catch.
- **Stretch:** the cleaning is idempotent: running it twice gives identical output (test it).

### C. Metrics and correctness

- **Must:** at least **5 metrics** defined in `METRICS.md` (name, formula, grain, filter,
  edge cases, owner), each implemented once in code and reused everywhere.
- **Must:** a **grain and fan-out check** (da.06) for every join, with a test that row
  counts and totals are unchanged by the join.
- **Must:** **reconciliation**: the headline numbers computed in two independent ways
  (pandas and SQL, or pandas and Excel) and shown to agree, with the tolerance.
- **Must:** at least one metric that is **not additive** (a ratio, a distinct count or a
  median) handled correctly at every level of aggregation.
- **Should:** a golden file of expected values that a test compares after every rerun.
- **Stretch:** a metric tree showing which lower metrics add up to the headline.

### D. SQL and the analysis layer

- **Must:** the clean data loaded into SQLite or DuckDB; at least **5 analytical queries**
  using joins, window functions and CTEs (da.07), kept in `sql/` and each reproduced in
  pandas.
- **Must:** each query has a comment with the question it answers and its grain.
- **Should:** one query checked with `EXPLAIN` and made faster with an index or a rewrite,
  with before and after timings (machine-specific values marked).
- **Stretch:** a view layer: base tables, then metric views, then a reporting view.

### E. Statistical reasoning

- **Must:** the pre-registered hypotheses of `QUESTION.md` tested, with the test chosen and
  justified, the **effect size** and a **confidence interval** (not only a p-value), and a
  check of the assumptions (da.08).
- **Must:** at least one **bootstrap** or permutation interval for a statistic with no
  simple formula (a median, a ratio).
- **Must:** a section on what could be **wrong**: confounders, selection, survivorship,
  multiple comparisons, a definition that changed in the period (da.06, da.08, da.11).
- **Should:** a comparison of at least two groups with the difference shown as an interval,
  and a practical judgement: is the difference big enough to matter?
- **Stretch:** a simulation that checks the false-positive rate of your own procedure.

### F. Visualisation and dashboard

- **Must:** at least **6 figures**, each with a title that states the finding, labelled axes
  with units, a sensible baseline, colour-blind-safe colours and alt text (da.09).
- **Must:** **a dashboard** (one page, Power BI per da.13, or an Excel report per da.12, or
  Streamlit or Plotly) with 4 KPI cards, 3-4 visuals, slicers, and a validation view whose
  numbers match your pandas figures.
- **Must:** the dashboard is built on a star schema (da.13): grain of every table written
  down, keys tested, measures defined once; model spec and answer file included.
- **Should:** a figure that shows uncertainty (intervals, a fan, bootstrap samples).
- **Stretch:** an interactive version that runs offline.

### G. The written report

- **Must:** `REPORT.md` of **6-10 pages** with: executive summary (the answer in five
  lines), the question and why it matters, data and cleaning in one page, methods, results
  with figures, limits, and a recommendation with the **next action and its owner**
  (da.10, da.11).
- **Must:** every number in the report is produced by code and **traceable**: a table
  `number -> script -> line or function`, or the numbers inserted automatically.
- **Must:** an honest limits section: what the data cannot say, which results are
  fragile, what would change the conclusion.
- **Should:** a one-page version for a non-technical manager, with no jargon.
- **Stretch:** a 5-minute presentation script with three slides.

### H. Reproducibility and engineering

- **Must:** one command (`make all`, or `python run_all.py`) rebuilds clean data, metrics,
  tables, figures and the report numbers from the raw files; the README says how long it
  takes (machine-specific).
- **Must:** a pinned `requirements.txt`, a fixed random seed for every random step, and the
  Python version recorded.
- **Must:** a small **test suite** (`pytest`): cleaning rules, join checks, metric
  functions against hand-calculated cases, and the reconciliation checks.
- **Must:** git history with many small commits and clear messages, no secrets, no
  machine-specific paths, and the large data files ignored (`.gitignore`) but described.
- **Should:** notebooks only for exploration; the final analysis lives in modules.
- **Should:** `ruff` clean and type hints on the metric functions.
- **Stretch:** a one-page `LIMITS_AND_NEXT.md` listing what you would do with another month.

## How the review works

1. **Question review** (before analysis): the reviewer reads `QUESTION.md` and asks
   questions. Typical outcomes: "which decision changes if the answer is yes?", "what does
   'late' mean for a request that is reopened?", or "this metric has two definitions".
2. **Midpoint check:** the data are clean and reconciled, the metrics are defined and tested,
   and the first figures exist. The reviewer re-runs the pipeline and tries to break a metric.
3. **Final review:** run through the checklist above. For every unticked **Must** the
   reviewer gives a pointer, not a patch ("how many rows does the join add?").
4. **Fresh-machine test:** clone the repo into a new folder, follow only the README, and
   rebuild everything from the raw files. If you get stuck, the README is the bug.
5. **Challenge drill:** the reviewer picks three numbers from the report and asks "show me".
   You trace each one to a script and a raw row count within a few minutes. If you cannot,
   the traceability is the bug.

### Scoring (for yourself)

| Score | Meaning |
|---|---|
| All Musts, most Shoulds | DA capstone passed |
| All Musts only | Passed, but go back and add the missing polish and tests |
| Any Must missing | Not done yet. Finish those first |

Stretch items are for pride and for your portfolio, not for the pass mark.

## Why this capstone

Anyone can draw a chart from a clean file. An analyst is paid for the opposite: for a number
that the finance team cannot break, a clean-up that is written down, a result with an honest
interval, and a recommendation someone can act on on Monday. The reconciliation, the
traceable number and the limits section are the three habits to keep for life.
